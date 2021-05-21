from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import Context, Template
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from applications.alumniprofile.models import Profile
from .models import EmailTemplate


def is_superuser(user):
    return user.is_superuser


def get_rendered_emails(from_email, email_template, recipients):
    subject = email_template.subject

    body = email_template.body
    body_template = Template(body)

    messages = []

    for profile in recipients:
        context = Context({
            "profile": profile,
        })
        html_message = body_template.render(context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject,
            plain_message,
            from_email,
            [profile.email],
            [settings.BCC_EMAIL_ID],
        )
        email.attach_alternative(html_message, "text/html")
        messages.append(email)

    return messages


def send_verification_email(request, profile):
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'

    rendered_url = render_to_string('registration/url_password_reset_email.html', {
        'uid': urlsafe_base64_encode(force_bytes(profile.user.pk)),
        'user': profile.user,
        'token': default_token_generator.make_token(profile.user),
        'domain': current_site.domain,
        'protocol': protocol,
    })

    from_email = settings.DEFAULT_FROM_EMAIL
    to = [profile.email]

    subject = 'SAC IIITDMJ Portal Registration Successful!'

    html_message = render_to_string('registration/account_verification_email.html', {
        "name" : profile.name,
        "email" : profile.email,
        "from" : profile.year_of_admission,
        "to" : profile.batch.batch,
        "prog" : profile.programme,
        "branch" : profile.branch,
        "reg_no" : profile.reg_no,
        "roll_no" : profile.roll_no,
        "pass" : rendered_url,
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        from_email,
        to,
        [settings.BCC_EMAIL_ID],
    )
    email.attach_alternative(html_message, "text/html")

    print("sending email to {}".format(to))
    try:
        email.send()
    except Exception as error:
        print("Exception while sending mail to {}".format(to))
        print(error)


@login_required
@user_passes_test(
    is_superuser, redirect_field_name=None,
    login_url=reverse_lazy('home')
)
def index(request):
    return render(request, 'adminportal/index.html')


@login_required
@user_passes_test(
    is_superuser, redirect_field_name=None,
    login_url=reverse_lazy('home')
)
def registrations_index(request):
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(roll_no=request.POST.get('id'))
            if profile.verify is not None:
                raise RuntimeError("Invalid Verification request for {}".format(profile.roll_no))

            if 'approve' in request.POST:
                send_verification_email(request, profile)
                profile.verify = True
                messages.add_message(request, messages.SUCCESS, "Registration Success, Mail sent to {}".format(profile.name))

            elif 'decline' in request.POST:
                profile.verify = False
                messages.add_message(request, messages.SUCCESS, "Registration Declined for {}".format(profile.name))

            profile.save()
        except Exception:
            print(Exception)
            messages.add_message(request, messages.ERROR, "Something went wrong, contact the admins.")

        return redirect('adminportal:registrations')

    unregistered = Profile.objects.all().filter(verify=None).filter(mail_sent=False)

    context = {
        'pending': unregistered
    }
    return render(request, 'adminportal/registrations.html', context)


@login_required
@user_passes_test(
    is_superuser, redirect_field_name=None,
    login_url=reverse_lazy('home')
)
def mailservice_index(request):
    if request.method == 'POST':
        template_id = request.POST['template_id']
        programme = request.POST['programme']
        batch = request.POST['batch']
        branch = request.POST['branch']

        template = EmailTemplate.objects.get(template_id=template_id)
        recipients = Profile.objects.all()

        if programme:
            recipients = recipients.filter(programme=programme)
        if batch:
            recipients = recipients.filter(batch__batch=batch)
        if branch:
            recipients = recipients.filter(branch=branch)

        messages = get_rendered_emails(settings.DEFAULT_FROM_EMAIL, template, recipients)

        connection = mail.get_connection(fail_silently=True)
        connection.send_messages(messages)

        return redirect('adminportal:email_sent')

    email_templates = EmailTemplate.objects.all()
    programmes = Profile.objects.values_list('programme', flat=True).distinct()
    batches = Profile.objects.select_related('batch').values_list('batch__batch', flat=True).distinct()
    branches = Profile.objects.values_list('branch', flat=True).distinct()

    context = {
        'email_templates': email_templates,
        'programmes': programmes,
        'batches': batches,
        'branches': branches,
    }

    return render(request, 'adminportal/mailservice.html', context)


@login_required
@user_passes_test(
    is_superuser, redirect_field_name=None,
    login_url=reverse_lazy('home')
)
def email_sent(request):
    return render(request, 'adminportal/success.html')
