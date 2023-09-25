from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from utils.breadcrumb import BreadCrumbMixin
from utils.mongodb import mongo_db
from .forms import Userform, RegistrationUserForm
from .models import User


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = User
    permission_required = "accounts.delete_user"
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy('accounts:user_list')


class UserList(BreadCrumbMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/user_list.html'
    context_object_name = 'user'
    model = User
    paginate_by = 10
    permission_required = ('accounts.view_user',)
    redirect_field_name = reverse_lazy('index')

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/user_tr.html"
        else:
            return self.template_name

    def get_queryset(self):
        import online_users.models

        user_status = online_users.models. \
            OnlineUserActivity.get_user_activities(timedelta(seconds=30))
        users = [user.user.id for user in user_status]

        search = self.request.GET.get("search", '')

        queryset = User.objects.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search)
            | Q(username__icontains=search)
        )
        for i in queryset:
            if i.id in users:
                i.online = "True"

        if not self.request.user.is_superuser or not self.request.user.is_staff:
            queryset = queryset.filter(marketplace_id=self.request.user.marketplace_id)

        return queryset


class UserChange(BreadCrumbMixin,
                 LoginRequiredMixin,
                 PermissionRequiredMixin,
                 UpdateView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/user_change.html'
    permission_required = ('accounts.change_user',)

    model = User
    success_url = reverse_lazy('accounts:user_list')
    form_class = Userform

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        form.fields["user_permissions"]. \
            queryset = form.fields["user_permissions"] \
            .queryset.filter().exclude(
            Q(name__icontains="online")
            | Q(name__icontains="periodic")
            | Q(name__icontains="session")
            | Q(name__icontains="solar")
            | Q(name__icontains="solar")
            | Q(name__icontains="content")
            | Q(name__icontains="interval")
            | Q(name__icontains="clocked")
            | Q(name__icontains="crontab")
            | Q(name__icontains="log")
            | Q(name__icontains="items")
            | Q(name__icontains="note")
            | Q(codename__icontains="delete_orderimports")
            | Q(codename__icontains="change_orderimports"))
        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""

        password = self.request.POST.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                for message in e.messages:
                    messages.add_message(self.request,
                                         messages.WARNING,
                                         message)
                return render(self.request, self.template_name, {"form": form})
            self.object.set_password(password)
        else:
            self.object.password = User.objects. \
                get(pk=self.kwargs['pk']).password
        if not self.request.user.is_superuser:
            user = User.objects.get(id=self.object.id)
            self.object.is_active = user.is_active
            for i in user.groups.all():
                self.object.groups.add(i)
                self.object.save()
            self.object.user_permissions.set(user.user_permissions.all())

            self.object.is_staff = user.is_staff

            self.object.save()
            messages.add_message(self.request,
                                 messages.INFO,
                                 'User Successfully updated.')
            return HttpResponseRedirect(self.get_success_url())

        return super().form_valid(form)


class UserCreate(BreadCrumbMixin,
                 LoginRequiredMixin,
                 PermissionRequiredMixin,
                 CreateView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/create_user.html'
    context_object_name = 'user'
    permission_required = ('accounts.add_user',)
    model = User
    fields = "__all__"

    def post(self, request, *args, **kwargs):
        form = Userform(request.POST or None, request.FILES)
        password = request.POST["password"]
        try:
            validate_password(password)
        except ValidationError as e:
            for message in e.messages:
                messages.add_message(request,
                                     messages.WARNING,
                                     message)
            return render(request, self.template_name, {"form": form})
        if form.is_valid():
            user = form.save()
            user.set_password(password)
            user.marketplace = self.request.user.marketplace
            user.save()
            messages.add_message(request,
                                 messages.INFO,
                                 'User Successfully created.')

        else:
            return render(request, self.template_name, {"form": form})

        if request.POST.get("save_data"):

            return redirect("accounts:user_list")

        elif request.POST.get("save_edit"):
            return redirect("accounts:change_list", user.id)
        else:
            return redirect("accounts:user_create")


class UserLogs(BreadCrumbMixin,
               LoginRequiredMixin,
               PermissionRequiredMixin,
               View):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/user_logs.html'
    paginate_by = 50
    permission_required = ('accounts.view_user',)

    def get(self, request, *args, **kwargs):
        db = mongo_db()
        search = self.request.GET.get("search", "")
        order_id = request.GET.get("id", "")
        data = [
            {
                "$or": [
                    {
                        'updates': {"$regex": f".*{search}.*"}
                    }, {
                        'user': {"$regex": f".*{search}.*"}
                    },
                ]
            },

        ]
        if order_id:
            data.append({'instance_id': int(order_id)})
        data = {"$and": data}
        query = db.test1.find(data).sort('created_at', -1)
        page = request.GET.get('page', 1)
        if not page:
            page = 1
        items = [r for r in query]

        from utils.pagination_controller import pagination
        current_page = pagination(items,
                                  len(items),
                                  self.paginate_by,
                                  int(page))
        current_page.update(self.get_breadcrumb())

        if request.is_ajax():
            return render(request, "user/user_logs_tr.html", current_page)
        else:
            return render(request, self.template_name, current_page)


class GroupCreate(BreadCrumbMixin,
                  LoginRequiredMixin,
                  PermissionRequiredMixin,
                  CreateView):
    model = Group
    fields = "__all__"
    success_url = reverse_lazy("accounts:group_list")
    permission_required = ('auth.add_group',)

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        form.fields["permissions"].queryset = form.fields["permissions"] \
            .queryset.filter().exclude(
            Q(name__icontains="online")
            | Q(name__icontains="periodic")
            | Q(name__icontains="session")
            | Q(name__icontains="solar")
            | Q(name__icontains="solar")
            | Q(name__icontains="content")
            | Q(name__icontains="interval")
            | Q(name__icontains="clocked")
            | Q(name__icontains="crontab")
            | Q(name__icontains="log")
            | Q(name__icontains="items")
            | Q(name__icontains="note")
            | Q(codename__icontains="delete_orderimports")
            | Q(codename__icontains="change_orderimports"))
        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Group Successfully added.')
        return super().form_valid(form)


class GroupDeleteView(PermissionRequiredMixin, DeleteView):
    # specify the model you want to use
    model = Group
    permission_required = "auth.delete_group"
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy('accounts:group_list')


class GroupList(BreadCrumbMixin, PermissionRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    template_name = 'auth/group_list.html'
    context_object_name = 'user'
    model = Group
    paginate_by = 10
    permission_required = ('auth.view_group',)
    redirect_field_name = reverse_lazy('index')

    def get_template_names(self):
        if self.request.is_ajax():
            return "include/group_tr.html"
        else:
            return self.template_name

    def get_queryset(self):
        search = self.request.GET.get("search", '')
        queryset = Group.objects.filter(
            Q(name__icontains=search) | Q(permissions__name__icontains=search)

        ).distinct()
        return queryset


class GroupChange(BreadCrumbMixin,
                  LoginRequiredMixin,
                  PermissionRequiredMixin,
                  UpdateView):
    model = Group
    fields = "__all__"
    success_url = reverse_lazy("accounts:group_list")
    permission_required = ('auth.change_group',)
    template_name = 'auth/form_update.html'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        form.fields["permissions"].queryset = form.fields["permissions"] \
            .queryset.filter().exclude(
            Q(name__icontains="online")
            | Q(name__icontains="periodic")
            | Q(name__icontains="session")
            | Q(name__icontains="solar")
            | Q(name__icontains="solar")
            | Q(name__icontains="content")
            | Q(name__icontains="interval")
            | Q(name__icontains="clocked")
            | Q(name__icontains="crontab")
            | Q(name__icontains="log")
            | Q(name__icontains="items")
            | Q(name__icontains="note")
            | Q(codename__icontains="delete_orderimports")
            | Q(codename__icontains="change_orderimports"))
        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        messages.add_message(self.request,
                             messages.INFO,
                             'Group Successfully added.')
        return super().form_valid(form)


class ProfileObjectMixin(SingleObjectMixin):
    """
    Provides views with the current user's profile.
    """
    model = User

    def get_object(self):
        """Return's the current users profile."""
        try:
            return self.request.user
        except User.DoesNotExist:
            pass


class UserProfile(BreadCrumbMixin,
                  ProfileObjectMixin,
                  LoginRequiredMixin,
                  UpdateView):
    login_url = reverse_lazy('login')
    redirect_field_name = 'redirect_to'
    template_name = 'user/user_change.html'
    model = User
    success_url = reverse_lazy('accounts:profile')
    form_class = Userform

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)  # Get the form as usual
        form.fields["user_permissions"]. \
            queryset = form.fields["user_permissions"] \
            .queryset.filter().exclude(
            Q(name__icontains="online")
            | Q(name__icontains="periodic")
            | Q(name__icontains="session")
            | Q(name__icontains="solar")
            | Q(name__icontains="solar")
            | Q(name__icontains="content")
            | Q(name__icontains="interval")
            | Q(name__icontains="clocked")
            | Q(name__icontains="crontab")
            | Q(name__icontains="log")
            | Q(name__icontains="items")
            | Q(name__icontains="note")
            | Q(codename__icontains="delete_orderimports")
            | Q(codename__icontains="change_orderimports"))
        return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""

        self.kwargs.update({"pk": self.request.user.id})
        password = self.request.POST.get("password")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                for message in e.messages:
                    messages.add_message(self.request,
                                         messages.WARNING,
                                         message)
                return render(self.request, self.template_name, {"form": form})
            self.object.set_password(password)
        else:
            self.object.password = User.objects. \
                get(pk=self.kwargs['pk']).password
        if not self.request.user.is_superuser:
            user = User.objects.get(id=self.object.id)
            self.object.is_active = user.is_active
            for i in user.groups.all():
                self.object.groups.add(i)
                self.object.save()
            self.object.user_permissions.set(user.user_permissions.all())

            self.object.is_staff = user.is_staff
            messages.add_message(self.request,
                                 messages.INFO,
                                 'User Successfully updated.')
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())

        return super().form_valid(form)


class RegistrationView(CreateView):
    template_name = 'registration/registration.html'
    form_class = RegistrationUserForm
    success_url = reverse_lazy("login")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            messages.success(request, f'Your user has been created.')

        return redirect("login")

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data()
        if self.request.method == 'POST':
            form = RegistrationUserForm(self.request.POST)
            if form.is_valid():
                user = form.save()
                group = Group.objects.get(name='Normal')
                group.user_set.add(user)
                return redirect('login')
        else:
            form = RegistrationUserForm()
        context.update({
            'title': 'Register',
            'form': form
        })
        return context
