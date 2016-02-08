import uuid

from flask import (
    Blueprint,
    jsonify,
    request
)

from app import (notify_alpha_client, api_user)
from app.aws_sqs import add_notification_to_queue
from app.dao import (templates_dao)
from app.schemas import (
    email_notification_schema, sms_template_notification_schema)

notifications = Blueprint('notifications', __name__)


@notifications.route('/<notification_id>', methods=['GET'])
def get_notifications(notification_id):
    return jsonify(notify_alpha_client.fetch_notification_by_id(notification_id)), 200


@notifications.route('/sms', methods=['POST'])
def create_sms_notification():
    resp_json = request.get_json()

    notification, errors = sms_template_notification_schema.load(resp_json)
    if errors:
        return jsonify(result="error", message=errors), 400
    template_id = notification['template']
    # TODO: remove once beta is reading notifications from the queue
    message = templates_dao.get_model_templates(template_id).content

    add_notification_to_queue(api_user['client'], template_id, 'sms', notification)
    # TODO: remove once beta is reading notifications from the queue
    return jsonify(notify_alpha_client.send_sms(
        mobile_number=notification['to'], message=message)), 200


@notifications.route('/email', methods=['POST'])
def create_email_notification():
    resp_json = request.get_json()
    notification, errors = email_notification_schema.load(resp_json)
    if errors:
        return jsonify(result="error", message=errors), 400
    # At the moment we haven't hooked up
    # template handling for sending email notifications.
    add_notification_to_queue(api_user['client'], "admin", 'email', notification)
    return jsonify(notify_alpha_client.send_email(
        notification['to_address'],
        notification['body'],
        notification['from_address'],
        notification['subject']))


@notifications.route('/sms/service/<service_id>', methods=['POST'])
def create_sms_for_service(service_id):

    resp_json = request.get_json()

    notification, errors = sms_template_notification_schema.load(resp_json)
    if errors:
        return jsonify(result="error", message=errors), 400

    template_id = notification['template']
    job_id = notification['job']

    # TODO: job/job_id is in notification and can used to update job status

    # TODO: remove once beta is reading notifications from the queue
    template = templates_dao.get_model_templates(template_id)

    if template.service.id != uuid.UUID(service_id):
        message = "Invalid template: id {} for service id: {}".format(template.id, service_id)
        return jsonify(result="error", message=message), 400

    # Actual client is delivery app, but this is sent on behalf of service
    add_notification_to_queue(service_id, template_id, 'sms', notification)

    # TODO: remove once beta is reading notifications from the queue
    content = template.content
    return jsonify(notify_alpha_client.send_sms(
        mobile_number=notification['to'], message=content)), 200
