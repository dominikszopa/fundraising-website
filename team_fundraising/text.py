
class Donation_text:

    # Shown as a message across the top of the page on return from a donation
    # used in views.py:new_donation()
    thank_you = (
        "Thank you for your donation. "
        "You may need to refresh this page to see the donation."
    )

    confirmation_email_subject = (
        'Thank you for donating to the Triple Crown for Heart! '
    )

    # Start of the email sent confirming the paypal payment has gone through
    # used in paypal.py:process_paypal()
    confirmation_email_opening = (
        'Thank you for your donation of '
    )

    # Closing of the email sent confirming the paypal payment has gone through
    # used in paypal.py:process_paypal()
    confirmation_email_closing = (
        '.\n\nFor all donations over $20, you will receive a tax receipt for '
        'the 2019 tax year.'
        '\nYour PayPal receipt should arrive in a separate email.\n'
    )

    notification_email_subject = (
        "You got a donation!"
    )

    notification_email_opening = (
        "Great news! You've just received a donation of "
    )

    notification_email_closing = (
        "\n\nAwesome work. It might be a good idea to send them a thank you."
    )


class Fundraiser_text:

    # Subject of the email sent on signup
    signup_email_subject = (
        "Welcome to fundraising for the Triple Crown for Heart!"
    )

    # Start of the email sent when someone signs up
    # used in views.py:signup()
    signup_email_opening = (
        "Thanks for signing up to fundraise with us!\n"
        "Your fundraising page can be found at:\n"
    )

    # Closing of the email sent when someone signs up
    # used in views.py:signup()
    signup_email_closing = (
        '\n\nYou can change your information by using the "Login" at the top.'
        '\n\nThe easiest way to start fundraising is to post on social media '
        'or write a short email to your friends telling them about your ride.'
        '\nDon\'t forget to include the url to your page!\n'
    )

    # Message show at the top of the fundraiser page after signing up
    # used in views.py:signup()
    signup_return_message = (
        "Thank you for signing up. Sharing your fundraiser page on social "
        "media or over email is the best way to get donations."
    )
