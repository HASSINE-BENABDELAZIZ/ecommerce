from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.paginator import Paginator, Page

from utils.mongodb import mongo_db


def pagination(list_items, total, page_size, page):
    try:
        items_count = list_items.count()
    except Exception:
        items_count = len(list_items)
    paginator = Paginator(list_items, page_size)
    try:
        list_items = paginator.page(page)

    except PageNotAnInteger:
        list_items = paginator.page(1)
    except EmptyPage:
        list_items = paginator.page(paginator.num_pages)

    if items_count % page_size == 0:
        list_items.paginator.num_pages = items_count // page_size
    else:
        list_items.paginator.num_pages = items_count // page_size + 1
    list_items.number = int(page)

    return {'is_paginated': list_items.paginator.count > 1,
            "items_count": items_count,
            "page_obj": list_items,
            "total": total}


def pagination_mongo(db_name, query, page_size, page):
    db = mongo_db()
    total = db[db_name].count()
    queryset = db.orders.find(query). \
        sort('created_at', -1). \
        skip(page_size * (int(page) - 1)).limit(page_size)
    items_count = queryset.count()
    queryset = [item for item in queryset]
    paginator = Paginator(queryset, page_size)
    try:
        list_items = paginator.page(page)

    except PageNotAnInteger:
        list_items = paginator.page(1)
    except EmptyPage:
        list_items = paginator.page(paginator.num_pages)

    if items_count % page_size == 0:
        list_items.paginator.num_pages = items_count // page_size
    else:
        list_items.paginator.num_pages = items_count // page_size + 1
    list_items.number = int(page)

    return {'is_paginated': list_items.paginator.count > 1,
            "items_count": items_count,
            "page_obj": list_items,
            "total": total}


class DSEPaginator(Paginator):

    def __init__(self, *args, **kwargs):
        super(DSEPaginator, self).__init__(*args, **kwargs)
        self._count = self.object_list.hits.total

    def page(self, number):
        number = self.validate_number(number)
        return Page(self.object_list, number, self)


def paginationES(list_items, items_count, total, page_size, page):
    list_items = list({v['order'].id: v for v in list_items}.values())
    total = len(list_items)
    paginator = Paginator(list_items, page_size)

    try:
        list_items = paginator.page(page)

    except PageNotAnInteger:
        list_items = paginator.page(1)
    except EmptyPage:
        list_items = paginator.page(paginator.num_pages)

    if items_count % page_size == 0:
        list_items.paginator.num_pages = total // page_size
    else:
        list_items.paginator.num_pages = total // page_size + 1
    list_items.number = int(page)
    for _ in list_items:
        break

    return {'is_paginated': list_items.paginator.count > 1,
            "items_count": items_count,
            "page_obj": list_items,
            "total": total}
