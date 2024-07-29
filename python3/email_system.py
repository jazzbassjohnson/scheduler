from python3.traveling_zip import Order


# Given we are not in a Django environment, we need to mock the send_mail function.
# from django.core.mail import send_mail
#
def send_email(to: str, subject: str, body: str):
	print(f"Sending email to: {to}")
	print(f"Subject: {subject}")
	print(f"Body: {body}")


# send_mail(subject, body, from_email)


def calculate_estimated_time(distance: float, speed: float) -> float:
	"""
    Calculate the estimated delivery time.

    Args:
        distance (float): The distance to the hospital in meters.
        speed (float): The speed of the Zip in meters per second.

    Returns:
        float: The estimated delivery time in seconds.
    """
	return distance / speed


def compose_email(hospital_name: str, estimated_time: float) -> str:
	"""
    Compose the email content.

    Args:
        hospital_name (str): The name of the hospital.
        estimated_time (float): The estimated delivery time in seconds.

    Returns:
        str: The email content.
    """
	estimated_time_minutes = estimated_time / 60  # Convert seconds to minutes
	email_content = f"Dear {hospital_name},\n\n"
	email_content += f"Your delivery is estimated to arrive in {estimated_time_minutes:.2f} minutes.\n"
	email_content += "Thank you for using our service.\n\n"
	email_content += "Best regards,\n"
	email_content += "Zipline Team"
	return email_content


def send_delivery_email(hospital_email: str, hospital_name: str, estimated_time: float):
	"""
    Send the delivery email to the hospital.

    Args:
        hospital_email (str): The email address of the hospital.
        hospital_name (str): The name of the hospital.
        estimated_time (float): The estimated delivery time in seconds.
    """
	email_content = compose_email(hospital_name, estimated_time)
	send_email(
		to=hospital_email,
		subject="Estimated Delivery Time",
		body=email_content
	)


def notify_hospital(order: Order, distance: float, speed: float):
	"""
		Notify the hospital of the estimated delivery time.

    Args:
        order (Order): The order object containing hospital information.
        distance (float): The distance to the hospital in meters.
        speed (float): The speed of the Zip in meters per second.
    """
	estimated_time = calculate_estimated_time(distance, speed)
	# if hospital has an email, send an email
	if order.hospital.email:  # hospital would need to have an email address
		send_delivery_email(order.hospital.email, order.hospital.name, estimated_time)
