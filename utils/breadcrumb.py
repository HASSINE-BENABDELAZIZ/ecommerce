from django.views import generic

from .models import BreadcrumbModel


class BreadCrumbMixin(generic.base.ContextMixin):
    modelurl = BreadcrumbModel

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(BreadCrumbMixin, self).get_context_data(**kwargs)
        request = self.request
        item_url = request.path
        item, created = self.modelurl.objects.get_or_create(url=item_url)
        item_url = item_url.split("/")
        big_table = []
        if len(item_url) == "2":
            big_table.append('Home:/:active')
        else:
            big_table.append('Home:/:inactive')

        if created:
            for sub_url_number in range(1, len(item_url) - 2):
                sub_url = "/"
                for i in range(1, sub_url_number + 1):
                    sub_url += item_url[i] + "/"
                big_table. \
                    append(f'{item_url[sub_url_number]}:{sub_url}:inactive')
            big_table.append(f'{item_url[-2]}:{request.path}:active')
            item.utility = big_table
            item.save()
        item.utility = [sub_element.split(":") for sub_element in item.utility]
        context.update({'breadcrumbs': item})

        return context

    def get_breadcrumb(self, **kwargs):
        # Call the base implementation first to get a context
        request = self.request
        item_url = request.path
        item, created = self.modelurl.objects.get_or_create(url=item_url)
        item_url = item_url.split("/")
        big_table = []
        if len(item_url) == "2":
            big_table.append('Home:/:active')
        else:
            big_table.append('Home:/:inactive')

        if created:
            for sub_url_number in range(1, len(item_url) - 2):
                sub_url = "/"
                for i in range(1, sub_url_number + 1):
                    sub_url += item_url[i] + "/"
                big_table.append(f'{item_url[sub_url_number]}:'
                                 f'{sub_url}:inactive')
            big_table.append(f'{item_url[-2]}:{request.path}:active')
            item.utility = big_table
            item.save()
        item.utility = [sub_element.split(":") for sub_element in item.utility]
        return {'breadcrumbs': item}
