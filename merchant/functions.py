from django.shortcuts import render, redirect
from admin import views
# Create your views here.

from django.http import HttpResponse, Http404, JsonResponse
from website.models import *
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage

from datetime import datetime, timedelta
from django.utils import timezone
import pytz
import json, os
from django.core.serializers.json import DjangoJSONEncoder
import requests
from sender import Mail, Message

# 0 Admin, 1 Customer, 2 Merchant, 3 Advertiser
def check_rule(request):
    if 'user' in request.session:
        user = request.session.get('user')
        print(user['role'])
        if 2 in user['role'] or 3 in user['role']:
            print(user)
            return 1
        return 0
    return 0


############
#############
###########
############
############
####
####
########

def account_services(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == 'GET':
        if request.GET.get('service') == 'available':
            if request.GET.get('table') == 'true':
                list_acc_ser = []
                account_services = Account_Service.objects.filter(account__id=request.session.get('user')['id'], remain__gt=0)
                for item in account_services:
                    acc_ser = []
                    acc_ser.append('<a href="/merchant/purchase_service/'+ str(item.service_id) +'"> TD'+ str(item.service_id) +'</a>')
                    acc_ser.append(item.service.service_name)
                    acc_ser.append(str(item.remain)+ ' tin')
                    acc_ser.append(str(item.service.day_limit) + ' ngày')
                    list_acc_ser.append(acc_ser)
                return HttpResponse(json.dumps(list_acc_ser), content_type="application/json")

            account_services = Account_Service.objects.filter(account__id=request.session.get('user')['id'], remain__gt=0)
            list_account_service = []
            for account_service in account_services:
                dict_account_service = dict()
                dict_account_service['post_id'] = account_service.pk
                dict_account_service['account_id'] = account_service.account_id
                dict_account_service['service_id'] = account_service.service_id
                dict_account_service['service_name'] = Service.objects.get(pk=account_service.service_id).service_name
                dict_account_service['remain'] = account_service.remain
                list_account_service.append(dict_account_service)
            return HttpResponse(json.dumps(list_account_service), content_type="application/json")
    return HttpResponse('Error')



####
####
####
####
####
####
####
####
####
####
####
####
####
####

def categorys(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method  == 'GET':
        if 'keyword' in request.GET:
            return HttpResponse(serialize('json', Category.objects.filter(name_category__icontains=request.GET.get('keyword'))), content_type="application/json")
        return HttpResponse(serialize('json', Category.objects.all()), content_type="application/json")


def attributes(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    return HttpResponse(serialize('json', Attribute.objects.filter(is_active=True)), content_type="application/json")


####  _______________Product
####
####
####
####
####
####
####
####
####

@csrf_exempt
def upload_image(request):
    if check_rule(request) == 0:
        return HttpResponse(-3)
    if request.method == 'POST' and request.FILES['photo']:
        myfile = request.FILES['photo']
        validate_image = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']
        print(myfile.size)
        if myfile.size > 2000000:
            return HttpResponse(-2)

        if myfile.content_type in validate_image:
            fs = FileSystemStorage(location=settings.BASE_DIR + '/media/product')
            filename = fs.save(myfile.name, myfile)
            image = Image(
                image_link=filename,
                user_id=Account.objects.get(pk=request.session.get('user')['id']),
            )
            image.save()
            return HttpResponse(image.id)
        else:
            return HttpResponse(0)
    return HttpResponse(-1)
        
@csrf_exempt
def del_image(request, id_image):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'DELETE':
        image = Image.objects.get(pk=int(id_image))
        path = settings.BASE_DIR + '/media/product' + image.image_link.url
        if os.path.exists(path):
            os.remove(path)
            image.delete()
            return HttpResponse('Xóa thành công')
        return HttpResponse('Lỗi hệ thống!\nChúng tôi sẽ cải thiệt chúng')
        
@csrf_exempt   
def product_add(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == "POST":
        count_product = request.POST.get('inputCountProduct')
        if int(count_product) < 1:
            return HttpResponse('Không thể tạo mới sản phẩm')

        count_tag = request.POST.get('inputCountTag')
        if int(count_tag) > 3:
            return HttpResponse('Không thể tạo mới sản phẩm')
        
        count_category = request.POST.get('inputCountCategory')
        if int(count_category) > 2 or int(count_category) < 1:
            return HttpResponse('Không thể tạo mới sản phẩm')
        
        count_images = request.POST.get('inputCountImage')
        if int(count_images) < 1:
            return  HttpResponse('Không thể tạo mới sản phẩm')

        discount_percent = request.POST.get('inputDiscount')
        if int(discount_percent) == '':
            return  HttpResponse('Không thể tạo mới sản phẩm')

        code = request.POST.get('inputCode')
        name = request.POST.get('inputName')
        detail = request.POST.get('inputDetail')
        origin = request.POST.get('inputOrigin')
        account_created = Account.objects.get(pk=request.session.get('user')['id'])
        product_config = Product(
            code=code,
            name= name,
            detail=detail,
            origin=origin,
            type_product=True,
            price=0,
            discount_percent=discount_percent,
            archive=False,
            account_created=account_created,
        )
        product_config.save()


        for i in range(int(count_category)):
            id = request.POST.get('inputCategory['+ str(i) +']')
            product_category = Product_Category(
                product_id = product_config,
                category_id = Category.objects.get(pk=int(id))
            )
            product_category.save()

        for i in range(int(count_tag)):
            key = request.POST.get('inputTag['+ str(i) +']')
            tag = Tag(
                tag_key = key,
                tag_value = product_config.id,
                tag_type=1,
            )
            tag.save()


        count_images = request.POST.get('inputCountImage')
        for i in range(int(count_images)):
            id = request.POST.get('inputImage['+ str(i) +']')
            image = Product_Image(
                product_id = product_config,
                image_id = Image.objects.get(pk=int(id))
            )
            image.save()

        v = 1
        min_price = []
        for i in range(int(count_product)):
            min_price.append(int(request.POST.get('inputVersion['+ str(i) +'][price]')))
            if count_product != 1:
                name_type = name + ' .v' + str(v)
            else: 
                name_type = name
            product = Product(
                code=code,
                name=name_type,
                detail=detail,
                origin=origin,
                price=request.POST.get('inputVersion['+ str(i) +'][price]'),
                discount_percent=discount_percent,
                type_product=False,
                archive=False,
                account_created=account_created,
            )
            product.save()
            
            Link_Type.objects.create(product_id=product, parent_product=product_config.id)

            data = request.POST.get('inputVersion['+ str(i) +'][value]')
            list_attr = data.split(' | ')
            attr = Attribute.objects.filter(is_active=True)
            index = 0
            for item in list_attr:
                product_attr = Product_Attribute(
                    product_id=product,
                    attribute_id=attr[index],
                    value=item,
                )
                product_attr.save()
                index = index + 1 
            v = v + 1

            product_config.price  = min(min_price)
            product_config.save()

        return HttpResponse(1)



@csrf_exempt
def product(request, id_product):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        #### 
        if request.GET.get('posted') == 'true':
            if Product.objects.filter(pk=id_product).exists() == False:
                return HttpResponse('Sản phẩm không tồn tại')
                product = Product.objects.get(pk=id_product).__dict__
                del product['_state']
                product_image = Product_Image.objects.filter(product_id=int(id_product), archive=False).order_by('image_id_id')
                list_image = []
                for item in product_image:
                    image = Image.objects.get(pk=item.image_id_id).__dict__
                    del image['_state']
                    list_image.append(image)
                product['images'] = list_image

                link_type = Link_Type.objects.filter(parent_product=int(id_product), product_id__archive=False)
                list_attr = []
                list_price = []
                for item in link_type:
                    list_price.append(item.product_id.price)
                product['list_price'] = list_price
                product['price_max_min'] = [max(list_price), min(list_price)]

                return  HttpResponse(json.dumps(product, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")

        product = Product.objects.get(pk=id_product).__dict__
        del product['_state']
        product_category = Product_Category.objects.filter(product_id=int(id_product), archive=False)
        list_category = []
        for item in product_category:
            category = Category.objects.get(pk=item.category_id_id).__dict__
            del category['_state']
            list_category.append(category)
        product['categories'] = list_category

        product_image = Product_Image.objects.filter(product_id=int(id_product), archive=False).order_by('image_id_id')
        list_image = []
        for item in product_image:
            image = Image.objects.get(pk=item.image_id_id).__dict__
            del image['_state']
            list_image.append(image)
        product['images'] = list_image

        tags = Tag.objects.filter(tag_type=1, tag_value=product['id'], archive=False)
        list_tag = []
        for item in tags:
            tag = item.__dict__
            del tag['_state']
            list_tag.append(tag)
        product['tags'] = list_tag

        #lay ra danh sach phien ban
        link_type = Link_Type.objects.filter(parent_product=int(id_product), product_id__archive=False)
        list_attr = []
        list_price = []
        for item in link_type:
            list_tmp = []
            list_price.append(item.product_id.price)
            product_attr = Product_Attribute.objects.filter(product_id=item.product_id.id, archive=False).order_by('attribute_id')
            for item in product_attr:
                list_tmp.append(item.value)
            list_attr.append(list_tmp)
    
        #su dung matrix de tra ve danh sach gia tri cho tung thuoc tinh
        len_atr = len(list_attr[0])
        len_verison = len(list_attr)
        list_value_attr = []
        for i in range(len_atr):
            list_temp = []
            for j in range(len_verison):
                if list_attr[j][i] not in list_temp:
                    list_temp.append(list_attr[j][i])
            list_value_attr.append(list_temp)

        product['list_attr'] = list_value_attr
        product['list_price'] = list_price
        product['price_max_min'] = [max(list_price), min(list_price)]

        return  HttpResponse(json.dumps(product, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")

    # Request POST
    if request.method == 'POST':
        if Product.objects.filter(pk=id_product, archive=False).exists() == False:
            return HttpResponse('Không tồn tại sản phẩm')
        now = timezone.now()
        product = Product.objects.get(pk=id_product)
        if product.is_activity == False:
            return HttpResponse('Sản phẩm đã bị khóa không cho phép sửa!')
        
        count_product = request.POST.get('inputCountProduct')
        if int(count_product) < 1:
            return HttpResponse('Không thể sửa sản phẩm')

        count_tag = request.POST.get('inputCountTag')
        if int(count_tag) > 3:
            return HttpResponse('Không thể sửa sản phẩm')
        
        count_category = request.POST.get('inputCountCategory')
        if int(count_category) > 2 or int(count_category) < 1:
            return HttpResponse('Không thể sửa sản phẩm')
        
        count_images = request.POST.get('inputCountImage')
        if int(count_images) < 1:
            return HttpResponse('Không thể sửa sản phẩm')

        discount_percent = request.POST.get('inputDiscount')
        if int(discount_percent) == '':
            return HttpResponse('Không thể sửa sản phẩm')
        

        product_link = Link_Type.objects.filter(parent_product=product.id, product_id__archive=False).values_list('product_id_id')
        Product.objects.filter(pk__in=product_link).update(archive=True, archive_at=now)
        Product_Category.objects.filter(product_id_id=product.id, archive=False).update(archive=True, archive_at=now)
        Product_Image.objects.filter(product_id_id=product.id, archive=False).update(archive=True, archive_at=now)
        Product_Attribute.objects.filter(product_id_id__in=product_link, archive=False).update(archive=True, archive_at=now)
        Tag.objects.filter(tag_type=1, tag_value=product.id, archive=False).update(archive=True, archive_at=now)

        #request 
        code = request.POST.get('inputCode')
        name = request.POST.get('inputName')
        detail = request.POST.get('inputDetail')
        discount_percent = request.POST.get('inputDiscount')
        origin = request.POST.get('inputOrigin')
        account_created = Account.objects.get(pk=request.session.get('user')['id'])
        
        # Edit product origin
        product.code=code
        product.name= name
        product.detail=detail
        product.origin=origin
        product.discount_percent=discount_percent
        product.save()

        for i in range(int(count_category)):
            id_category = request.POST.get('inputCategory['+ str(i) +']')
            product_category = Product_Category(
                product_id = product,
                category_id = Category.objects.get(pk=int(id_category))
            )
            product_category.save()

        for i in range(int(count_tag)):
            key = request.POST.get('inputTag['+ str(i) +']')
            tag = Tag(
                tag_key = key,
                tag_value = product.id,
                tag_type=1,
            )
            tag.save()


        for i in range(int(count_images)):
            id_image = request.POST.get('inputImage['+ str(i) +']')
            image = Product_Image(
                product_id = product,
                image_id = Image.objects.get(pk=int(id_image))
            )
            image.save()

        
        
        v = 1
        min_price = []
        for i in range(int(count_product)):
            min_price.append(int(request.POST.get('inputVersion['+ str(i) +'][price]')))
            if int(count_product) != 1:
                name_type = name + ' .v' + str(v)
            else: 
                name_type = name
            product2 = Product(
                code=code,
                name=name_type,
                detail=detail,
                origin=origin,
                price=request.POST.get('inputVersion['+ str(i) +'][price]'),
                discount_percent=discount_percent,
                type_product=False,
                archive=False,
                account_created=account_created,
            )
            product2.save()
            
            Link_Type.objects.create(product_id=product2, parent_product=product.id)
            
            data = request.POST.get('inputVersion['+ str(i) +'][value]')
            list_attr = data.split(' | ')
            attr = Attribute.objects.filter(is_active=True)
            index = 0
            for item in list_attr:
                product_attr = Product_Attribute(
                    product_id=product2,
                    attribute_id=attr[index],
                    value=item,
                )
                product_attr.save()
                index = index + 1 
            v = v + 1
        product.price  = min(min_price)
        product.save()

        return HttpResponse(1)
        

    if request.method == 'DELETE':
        # kiem tra san pham da duoc dang chua?
        # can huy goi tin de duoc xoa
        if Product.objects.filter(pk=id_product, archive=False).exists() == False:
            return HttpResponse('Sản phẩm không tồn tại!')
        try:
            now = timezone.now()
            product = Product.objects.get(pk=id_product)
            if product.is_activity == False:
                return HttpResponse('Sản phẩm đã bị khóa không cho phép xóa!')

            product.archive = True
            product.is_activity = False
            product.archive_at = now
            product.save()
            if Post_Product.objects.filter(product_id_id=product.id).exists() == True:
                Post_Product.objects.filter(product_id_id=product.id).update(is_lock=True, is_activity=False)
            return HttpResponse(1)
        except:
            return HttpResponse('Lỗi hệ thống!')
        return HttpResponse('Lỗi hệ thống!')


def products(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if request.GET.get('table') == 'true':
            products = []
            prod_all = Product.objects.filter(type_product=True, archive=False, account_created_id=request.session.get('user')['id']).order_by('-pk')
            for item in prod_all:
                if Link_Type.objects.filter(parent_product=item.id).exists() == True:
                    product = []
                    product.append('<a href="/merchant/product/edit/'+ str(item.id) +'">SP'+ str(item.id) +'</a>')
                    product.append(item.name)
                    product.append(str(item.price) + ' VND')
                    image = Product_Image.objects.filter(product_id_id=item.id, archive=False).order_by('image_id_id').first()
                    if Product_Image.objects.filter(product_id_id=item.id, archive=False).exists() == True:
                        product.append('<div class="tbl_thumb_product"><img src="/product' + image.image_id.image_link.url + '" /></div>')
                    else:
                        product.append('<div class="tbl_thumb_product"><img src="/static/website/images/product_1.jpg" /></div>')
                    
                    if Post_Product.objects.filter(product_id_id=item.id).exists() == False:
                        product.append('<label class="label label-warning">Chưa được đăng</label>')
                    else:
                        post = Post_Product.objects.filter(product_id_id=item.id).first()
                        if post.is_lock == True:
                            product.append('<label class="label label-info">Không hiển thị</label>')
                        else:
                            product.append('<label class="label label-success">Đang hiển thị</label>')
                    
                    if item.is_activity == 1:
                        product.append('<p style="color:green">Được hiển thị</p>')
                    if item.is_activity == 0:
                        product.append('<p style="color:red">Bị khóa</p>')
                    products.append(product)
            return HttpResponse(json.dumps(products), content_type="application/json")
        if request.GET.get('posted') == 'false':
            if 'include' in request.GET: 
                # http://localhost:8000/merchant/products?posted=false&include=id_product
                # lay danh sach san chua dang san pham do
                list_id = Post_Product.objects.values_list('product_id__id').filter(is_activity=True, is_lock=False).exclude(product_id__id=request.GET.get('include'))
                return HttpResponse(serialize('json', Product.objects.exclude(pk__in=list_id).filter(type_product=True)), content_type="application/json")
            list_id = Post_Product.objects.values_list('product_id__id').filter(is_activity=True, is_lock=False)
            return HttpResponse(serialize('json', Product.objects.exclude(pk__in=list_id).filter(type_product=True, is_activity=True, archive=False)), content_type="application/json")
        return HttpResponse(0)
    return HttpResponse(0)


### ----------------------Service
###
###
###
###
###
###
###
###
###

def services(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if 'table' in request.GET:
            if request.GET.get('table') == True:
                return HttpResponse(serialize('json', Service.objects.filter()), content_type="application/json")
    return HttpResponse(serialize('json', Service.objects.filter(is_active=True)), content_type="application/json")



def service(request, id_service):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == "GET":
        if 'posted' in request.GET:
            if request.GET.get('posted') == 'true':
                service = Service.objects.get(pk=id_service).__dict__
                del service['_state']
                return HttpResponse(json.dumps(service, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")

        if Service.objects.filter(pk=id_service, is_active=True).exists() == False:
            return HttpResponse(-1)
            
        service = Service.objects.get(pk=id_service).__dict__
        del service['_state']

        url = "http://data.fixer.io/api/latest?access_key=32893f56d737e115463ea1b87dd134b7&symbols=USD,EUR,VND&format=1"
        response = requests.get(url)
        data = json.loads(response.text)
        service['usd'] = (float(service['amount'])/ float(data['rates']['VND'])) * float(data['rates']['USD'])
        return HttpResponse(json.dumps(service, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")


@csrf_exempt        
def purchase_service(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
        
    if request.method == 'POST':
        ## chua kiem tra lai qua API PAYPAL ve ma Giao dich
        
        purchase_name = request.POST.get('inputPurchaseName')
        merchant_id = Account.objects.get(pk=request.session.get('user')['id'])
        service_id = request.POST.get('inputServiceId')
        amount = request.POST.get('inputAmount')
        state = request.POST.get('inputState')

        try:
            service = Service.objects.get(pk=service_id)
            purchase_service = Purchase_Service(
                purchase_name=purchase_name,
                merchant_id=merchant_id,
                service_id=service,
                amount=float(amount),
                state=int(state),
            )
            purchase_service.save()

            account_service = Account_Service.objects.filter(account__id=merchant_id.id, service__id=service.id)
            if account_service.count() == 1:
                remain = account_service[0].remain
                account_service.update(remain=remain+service.value)
                return HttpResponse('Dữ liệu tin đăng đã được cập nhật')
            return HttpResponse('Lỗi hệ thống!')
        except:
            return HttpResponse('Lỗi hệ thống!')
    return HttpResponse('Lỗi hệ thống!')


###
###
###
###-------  Post Product
###
###
###
###
###
###



@csrf_exempt 
def post_add(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == 'POST':
        product_id = request.POST.get('inputProduct')
        service_id = request.POST.get('inputService')
        creator_id = Account.objects.get(pk=request.session.get('user')['id'])

        if creator_id.token_ghtk == '':
            return HttpResponse(-4)

        # check  product 
        if Post_Product.objects.filter(product_id__id=product_id, is_activity=True, is_lock=False).exists():
            return HttpResponse('Lỗi sản phẩm bạn chọn đã được sử dụng!')
        # check remain post
        if Account_Service.objects.filter(service_id=int(service_id), account_id=creator_id, remain__gt=0).exists == False:
            return HttpResponse('Lỗi! Tin đăng không tồn tại!')

        product = Product.objects.get(pk=product_id)
        if product.account_created.id != creator_id.id:
            return HttpResponse('Sản phẩm không khả dụng')


        service = Service.objects.get(pk=int(service_id))
        quantity = request.POST.get('inputQuantity')


        if int(quantity) > service.quantity_product:
            return HttpResponse('Số lượng sản phẩm phải nhỏ hơn '+ str(service.quantity_product))
        if int(quantity) <= 0 or quantity == '':
            return HttpResponse('Số lượng sản phẩm phải lớn hơn 0')

    
        post_product = Post_Product(
            product_id = product,
            post_type = service,
            creator_id = creator_id,
            quantity = int(quantity),
            visable_vip = service.visable_vip,
            expire = datetime.now() + timedelta(days=service.day_limit),
        )
        post_product.save()

        account_service = Account_Service.objects.filter(account_id=creator_id, service_id=post_product.post_type_id)
        if account_service.count() == 1:        
            remain = account_service[0].remain
            account_service.update(remain=remain-1)
            return HttpResponse(1)
        return HttpResponse('Lỗi hệ thống')

    return HttpResponse('Lỗi hệ thống')


# def check_expire_post(id_post):
#     post = Post_Product.objects.get(pk=id_post)
#     if post.expire.replace(tzinfo=None) <= datetime.now():
#         post.update(is_lock=True, is_activity=False)


@csrf_exempt 
def post(request, id_post):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == 'GET':
        return HttpResponse(serialize('json', Post_Product.objects.filter(pk=id_post, creator_id__id=request.session.get('user')['id'])), content_type="application/json")

    if request.method == 'POST':
        # kiem tra tin dang co ton tai khong?
        if Post_Product.objects.filter(pk=id_post, creator_id__id=request.session.get('user')['id']).exists() == False:
            return HttpResponse('Tin đăng không tồn tại!')

        post = Post_Product.objects.get(pk=id_post)
        # kiem tra da het  hang cua
        if post.is_lock == True:
            return HttpResponse('Tin đăng đã bị khóa, Không được phép sửa!')

        quantity = request.POST.get('inputQuantity')

        if int(quantity) > (post.post_type.quantity_product - post.bought):
            return HttpResponse('Số lượng sản phẩm phải nhỏ hơn {}'.format(str(post.quantity - post.bought)))
        if int(quantity) <= 0 or quantity == '':
            return HttpResponse('Số lượng sản phẩm phải lớn hơn 0')

        post.quantity = quantity
        post.is_activity = request.POST.get('inputIsActivity')
        post.save()
        return HttpResponse(1)

    if request.method == 'DELETE':
        if Post_Product.objects.filter(pk=id_post, creator_id__id=request.session.get('user')['id']).exists() == False:
            return HttpResponse('Tin đăng không tồn tại!')
        post = Post_Product.objects.get(pk=id_post)
        if post.is_lock == True:
            return HttpResponse('Tin đăng đã khóa! Không thể ngừng hiển thị')
        if post.is_activity == False:
            return HttpResponse('Thực hiện thất bại!\nTin đăng đã tắt hiển thị')
        post.is_activity = False
        post.save()
        return HttpResponse(1)
    return
    
def posts(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == 'GET':
        posts = []
        post_all = Post_Product.objects.filter(creator_id__id=request.session.get('user')['id'])
        for item in post_all:
            post = []
            post.append('<a href="/merchant/post/edit/'+ str(item.id) +'"> TD'+ str(item.id) +'</a>')
            post.append('<a href="/merchant/product/edit/'+ str(item.product_id_id) +'"> SP'+ str(item.product_id_id) +'</a>')
            post.append(item.quantity - item.bought)
            post.append(item.expire.replace(tzinfo=None).strftime("%d/%m/%Y %H:%M"))
            post.append(item.post_type.service_name)
            if item.is_lock == False:
                if item.is_activity == True:
                    post.append('<label class="label label-success">Đang hiển thị</label>')
                else:
                    post.append('<label class="label label-info">Ngừng hiển thị</label>')
            else:
                if item.bought == item.quantity:
                    post.append('<label class="label label-danger">Hết hàng</label>')
                else:
                    post.append('<label class="label label-danger">SP bị xóa</label>')
            posts.append(post)
        return HttpResponse(json.dumps(posts), content_type="application/json")

### Ly Thanh
# Lý Thành

def payment_ads(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if request.GET.get('table') == 'true':
            list_payment = []
            payment_all = Purchase_Service_Ads.objects.filter(merchant_id_id=request.session.get('user')['id'])
            for item in payment_all:
                payment_item = []
                payment_item.append('<a href="/merchant/payment_ads_detail/'+ str(item.id) +'">'+ item.purchase_name +'</a>')
                payment_item.append('<a href="/admin/user/see/'+ str(item.merchant_id.id) +'">'+ item.merchant_id.name +'</a>')
                payment_item.append(str(item.amount) + ' VNĐ')
                payment_item.append(str(item.success_at.replace(tzinfo=None)).split(' ')[0]+ ' ' +str(item.success_at.replace(tzinfo=None)).split(' ')[1].split('.')[0])
                if item.state != 0:
                    payment_item.append('<label class="label label-success">Thanh toán thành công</label>')
                else:   
                    payment_item.append('<label class="label label-danger">Thanh toán thất bại</label>')
                list_payment.append(payment_item)
            return HttpResponse(json.dumps(list_payment, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")
        return HttpResponse('No data')
def f_payment_ads_detail(request, id_payment_ads):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if Purchase_Service_Ads.objects.filter(pk=id_payment_ads).exists() == False:
            return HttpResponse('Không tồn tại giao dịch!')
        payment =  Purchase_Service_Ads.objects.get(pk=id_payment_ads).__dict__
        del payment['_state']
        merchant = Account.objects.filter(pk=payment['merchant_id_id']).values('name', 'email')[0]
        #del merchant['_state']
        service = Service_Ads.objects.get(pk=payment['service_ads_id_id']).__dict__
        del service['_state']
        payment['merchant'] = merchant
        payment['service'] = service
        return HttpResponse(json.dumps(payment, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")

def f(x):
    return {
        1: "Đầu trang",
        2: "Giữa trang",
        3: "Cuối trang",
        4: "Slide",
        5: "Bên phải slide 1",
        6: "Bên phải slide 2",
    }[x]


def get_my_choices(id):
    _list = Service_Ads.objects.filter(position=f(id))
    return _list


def findByValue(input, value):
    for i in range(len(input)):
        if input[i]['value'] == value:
            return i
    return -1


@csrf_exempt
def getDateAvailable(request, position, id_ads):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        infor_ads = Service_Ads.objects.get(pk=id_ads)
        _list = Purchase_Service_Ads.objects.filter(
            service_ads_id__position=position)
        _input1 = []
        for item in _list:
            date_dict = dict()
            date_dict['start'] = item.date_start
            date_dict['end'] = item.date_start + \
                timedelta(days=item.service_ads_id.day_limit)
            _input1.append(date_dict)
        max_date = (datetime.now()+timedelta(days=120))
        min_date = datetime.now()+timedelta(days=3)
        step = timedelta(days=1)
        check = []
        while min_date <= max_date:
            date_dict = dict()
            date_dict['check'] = True
            date_dict['value'] = min_date.strftime('%Y-%m-%d')
            check.append(date_dict)
            min_date += step
        for item in _input1:
            while item['start'] < item['end']:
                check[findByValue(check, item['start'].strftime(
                    '%Y-%m-%d'))]['check'] = False
                item['start'] += step
        max_date = (datetime.now()+timedelta(days=120))
        min_date = datetime.now()+timedelta(days=3)
        result = []
        while min_date <= max_date:
            flag = True
            if check[findByValue(check, min_date.strftime('%Y-%m-%d'))]['check']:
                tempdate = min_date
                for i in range(infor_ads.day_limit):
                    if tempdate >= max_date:
                        break
                    if check[findByValue(check, tempdate.strftime('%Y-%m-%d'))]['check'] == False:
                        flag = False
                        break
                    tempdate += step
                if flag:
                    result.append(min_date.strftime('%Y-%m-%d'))
            min_date += step
        return HttpResponse(json.dumps(result), content_type="application/json")
    return HttpResponse(-1)


@csrf_exempt
def get_my_choices_2(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        ads = []
        for item in Service_Ads.objects.all():
            ads_dict = dict()
            ads_dict['id'] = item.id
            ads_dict['service_name'] = item.service_name
            ads_dict['position'] = item.position
            ads_dict['amount'] = item.amount
            ads_dict['day_limit'] = item.day_limit
            ads.append(ads_dict)
        return HttpResponse(json.dumps(ads), content_type="application/json")
    return HttpResponse(1)


@csrf_exempt
def upload_image_ads(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'POST' and request.FILES['photo']:
        myfile = request.FILES['photo']
        validate_image = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']
        print(myfile.size)
        if myfile.size > 1000000:
            return HttpResponse(-2)

        if myfile.content_type in validate_image:
            fs = FileSystemStorage(
                location=settings.BASE_DIR + '/media/ads')
            filename = fs.save(myfile.name, myfile)
            image = Image(
                image_link=myfile.name,
                user_id=Account.objects.get(
                    pk=request.session.get('user')['id']),
            )
            image.save()
            return HttpResponse(image.id)
        else:
            return HttpResponse(0)
    return HttpResponse(-1)


@csrf_exempt
def post_ads(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'POST':
        filename = ""
        filename_2 = ""
        filename_3 = ""
        myfile1 = request.FILES['inputPhoto_1']

        if request.FILES.get('inputPhoto_2', False):
            myfile2 = request.FILES['inputPhoto_2']
        if request.FILES.get('inputPhoto_3', False):
            myfile3 = request.FILES['inputPhoto_3']

        validate_image = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']
        # up load image 1 to server
        print(myfile1.size)
        if myfile1.size > 1000000:
            return HttpResponse(-2)
        if myfile1.content_type in validate_image:
            fs = FileSystemStorage(
                location=settings.BASE_DIR + '/media/ads')
            filename = fs.save(myfile1.name, myfile1)
        else:
            return HttpResponse(0)
        # upload image 2 to server
        if request.FILES.get('inputPhoto_2', False):
            print(myfile2.size)
            if myfile2.size > 1000000:
                return HttpResponse(-2)
            if myfile2.content_type in validate_image:
                fs = FileSystemStorage(
                    location=settings.BASE_DIR + '/media/ads')
                filename_2 = fs.save(myfile2.name, myfile2)
            else:
                return HttpResponse(0)
        # upload image 3 to server
        if request.FILES.get('inputPhoto_3', False):
            print(myfile3.size)
            if myfile3.size > 1000000:
                return HttpResponse(-2)
            if myfile3.content_type in validate_image:
                fs = FileSystemStorage(
                    location=settings.BASE_DIR + '/media/ads')
                filename_3 = fs.save(myfile3.name, myfile3)
            else:
                return HttpResponse(0)
        inputAds_id = request.POST.get('inputAds_id')

        inputLink_1 = request.POST.get('inputLink_1')
        inputLink_2 = request.POST.get('inputLink_2')
        inputLink_3 = request.POST.get('inputLink_3')

        inputContent_1 = request.POST.get('inputContent_1')
        inputContent_2 = request.POST.get('inputContent_2')
        inputContent_3 = request.POST.get('inputContent_3')

        service_ads = Purchase_Service_Ads.objects.get(id=inputAds_id)

        customer = Account.objects.get(pk=request.session.get('user')['id'])

        service_ads_post = Service_Ads_Post(
            service_name=service_ads.service_ads_id.service_name,
            purchase_service_id=service_ads,
            customer_id=customer,
            image_1=myfile1.name,
            image_1_url=inputLink_1,
            image_1_content=inputContent_1,
            image_2=None if not request.FILES.get('inputPhoto_2', False) else myfile2.name,
            image_2_url=inputLink_2,
            image_2_content=inputContent_2,
            image_3=None if not request.FILES.get('inputPhoto_3', False) else myfile3.name,
            image_3_url=inputLink_3 ,
            image_3_content=inputContent_3,
            state=1,
        )
        service_ads_post.save()

        Purchase_Service_Ads.objects.filter(id=inputAds_id).update(state=2)

        return redirect('/merchant/manager_ads_running')

    return HttpResponse(-1)


@csrf_exempt
def post_ads_2(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'POST':
        inputAds_id = request.POST.get('inputAds_id')

        image_1 = request.POST.get('inputPhoto_1')
        image_2 = request.POST.get('inputPhoto_2')
        image_3 = request.POST.get('inputPhoto_3')

        inputLink_1 = request.POST.get('inputLink_1')
        inputLink_2 = request.POST.get('inputLink_2')
        inputLink_3 = request.POST.get('inputLink_3')

        inputContent_1 = request.POST.get('inputContent_1')
        inputContent_2 = request.POST.get('inputContent_2')
        inputContent_3 = request.POST.get('inputContent_3')

        service_ads = Purchase_Service_Ads.objects.get(id=inputAds_id)

        customer = Account.objects.get(pk=request.session.get('user')['id'])

        expirired = service_ads.date_start + \
            timedelta(days=service_ads.service_ads_id.day_limit)

        service_ads = Service_Ads_Post(
            service_name=service_ads.service_ads_id.service_name,
            purchase_service_id=service_ads,
            customer_id=customer,
            image_1=image_1,
            image_1_url=inputLink_1,
            image_1_content=inputContent_1,
            image_2=image_2,
            image_2_url=inputLink_2,
            image_2_content=inputContent_2,
            image_3=image_3,
            image_3_url=inputLink_3 ,
            image_3_content=inputContent_3,
            expiried=expirired,
            is_active=True,
        )
        service_ads.save()
        return HttpResponse(1)    
    return HttpResponse(0)

@csrf_exempt
def del_image_ads(request, id_image):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'DELETE':
        image = Image.objects.get(pk=int(id_image))
        path = settings.BASE_DIR + '/media/ads' + image.image_link.url
        if Storage.exists(name=path):
            Storage.delete(path)
            image.delete()
        return HttpResponse('1')
    return HttpResponse('Error Request')


def getServiceAdsAvailable(id):
    result = Purchase_Service_Ads.objects.filter(merchant_id__id=id,state=1)
    if result:
        return result
    return None


@csrf_exempt
def purchase_service_ads(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')

    if request.method == 'POST':
        purchase_name = request.POST.get('inputPurchaseName')
        merchant_id = Account.objects.get(pk=request.session.get('user')['id'])
        service_ads_id = request.POST.get('inputServiceId')
        amount = request.POST.get('inputAmount')
        state = request.POST.get('inputState')
        date_start = datetime.strptime(request.POST.get('inputStart_date'), '%Y-%m-%d')

        try:
            purchase_service = Purchase_Service_Ads(
                purchase_name=purchase_name,
                merchant_id=merchant_id,
                service_ads_id=Service_Ads.objects.get(pk=service_ads_id),
                amount=amount,
                state=int(state),
                date_start=date_start,
            )
            purchase_service.save()
            body = "Thông tin thanh toán quảng cáo"
            content = "<html><head>"
            content += '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">'
            content += "</head><body>"
            content += "<table class='table'><thead><tr><th>Mã giao dịch</th><th>Mã dịch vụ</th><th>Người thanh toán</th><th>Tổng tiền</th></tr></thead>"
            content += "<tbody><tr class='success'><td>"+purchase_name+"</td><td>"+Service_Ads.objects.get(pk=service_ads_id).service_name+"</td><td>"+merchant_id.name+"</td><td>"+amount+"</td></tr></tbody>"
            content += "</table>"
            content += "</body></html>"
            send_email_notifile(merchant_id.email,body,content)
            return HttpResponse('Success!')
        except:
            return HttpResponse('Error!')
    return HttpResponse('Error Add Purchase!')

 
@csrf_exempt
def getAllAdsRunning(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    merchant_id = Account.objects.get(pk=request.session.get('user')['id'])
    mer_id = merchant_id.id
    if request.method == 'GET':
        result = []
        for item in Service_Ads_Post.objects.filter(customer_id__id=mer_id):
            post_dict = dict()
            post_dict['id'] = item.id
            post_dict['ads_name'] = "<a href='/merchant/manager_ads_running_detail/"+str(item.purchase_service_id.id)+"'>"+item.service_name+"</a>"
            post_dict['user'] = item.customer_id.name
            post_dict['date_start']=item.purchase_service_id.date_start.replace(tzinfo=None).strftime("%d/%m/%Y")
            post_dict['date_end'] = (item.purchase_service_id.date_start+timedelta(days=item.purchase_service_id.service_ads_id.day_limit)).replace(tzinfo=None).strftime("%d/%m/%Y")
            if item.state == "2" and item.purchase_service_id.state == "4":
                post_dict['status'] = "<label class='label label-success'>Đang chạy</label>"
            if item.state == "2" and item.purchase_service_id.state == "3":
                post_dict['status'] = "<label class='label label-success'>Đã duyệt - Chưa chạy</label>"
            if item.state == "1":
                post_dict['status'] = "<label class='label label-warning'>Đang duyệt</label>"
            if item.state == "-1":
                post_dict['status'] = "<label class='label label-danger'>Không duyệt</label>"
            result.append(post_dict)
        if result:
            return HttpResponse(json.dumps(result),content_type="application/json")
    
    return HttpResponse(-1)


@csrf_exempt
def getDetailRunning(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'POST':
        id = request.POST['inputID']
        post_ads = Service_Ads_Post.objects.filter(purchase_service_id__id=id).first()
        if post_ads:
            post_dict = dict()
            post_dict['id']=post_ads.id
            post_dict['img_1'] = post_ads.image_1
            post_dict['content_1']= post_ads.image_1_content
            post_dict['url_1']=post_ads.image_1_url
            post_dict['img_2'] = post_ads.image_2
            post_dict['content_2']= post_ads.image_2_content
            post_dict['url_2']=post_ads.image_2_url
            post_dict['img_3'] = post_ads.image_3
            post_dict['content_3']= post_ads.image_3_content
            post_dict['url_3']=post_ads.image_3_url
            return HttpResponse(json.dumps(post_dict),content_type="application/json")
    return HttpResponse(-1)


###  Order

def orders(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if request.GET.get('table') == 'true':
            list_order = []
            order_all_id = Order_Detail.objects.filter(merchant_id=request.session.get('user')['id']).values_list('order_id').distinct()
            print(order_all_id)
            order_all = Order.objects.filter(pk__in=order_all_id)
            for item in order_all:
                order = []
                order.append('<a href="/merchant/order/edit/'+ str(item.id) +'"> DH'+ str(item.id) +'</a>')
                order.append(item.customer.name)
                order.append(str(item.amount) + ' VND')
                #order.append(item.order.created.replace(tzinfo=None))
                order_detail = Order_Detail.objects.filter(order_id=item.id, merchant_id=request.session.get('user')['id']).first()
                if order_detail.state == '1':
                    order.append('<label class="label label-success">Thành công</label>')
                    order.append('<a href="/merchant/order/edit/'+ str(item.id) +'" class="btn btn-default">Đánh giá</a>')
                if order_detail.state == '0':
                    order.append('<label class="label label-danger">Hủy bỏ</label>')
                    order.append('<a href="/merchant/order/edit/'+ str(item.id) +'" class="btn btn-default">Đánh giá</a>')
                if order_detail.state == '2':
                    order.append('<label class="label label-info">Đặt hàng</label>')
                    order.append('<a onclick="change_state('+ str(item.id) +', 3)" class="btn btn-warning">Bắt đầu gói hàng</a>')
                if order_detail.state == '3':
                    order.append('<label class="label label-warning">Đang gói hàng</label>')
                    order.append('<a onclick="change_state('+ str(item.id) +', 4)" class="btn btn-info">Bắt đầu vận chuyển</a>')
                if order_detail.state == '4':
                    order.append('<label class="label label-default">Đang vận chuyển</label>')
                    order.append('<a onclick="change_state('+ str(item.id) +', 1)" class="btn btn-success">Thành công</a><a onclick="change_state('+ str(item.id) +', 0)"  style="margin-left: 10px;" class="btn btn-danger">Thất bại</a>')
                list_order.append(order)
            return HttpResponse(json.dumps(list_order, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")
    return

def change_state(request, id_order, state):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if Order.objects.filter(pk=id_order).exists() == False:
            return HttpResponse('Đơn hàng không tồn tại!')
        
        order = Order.objects.get(pk=id_order)
        order_detail = Order_Detail.objects.filter(order_id=order.id, merchant_id=request.session.get('user')['id']).exclude(state__in = [0, 1])
        if order_detail.count() == 0:
            return HttpResponse('Đơn hàng bị lỗi!')

        if state == 1:
            if order_detail.first().state != '4':
                return HttpResponse('Đơn hàng bị từ chối trạng thái thành công')
            order_detail.update(state=1)
            header = 'Đơn hàng bạn đã mua thành công vào lúc '+ str(datetime.now()) +' !'
            body = '<p>Vui lòng đánh giá người bán của chúng tôi <a href="/shop/'+ str(request.session.get('user')['id']) +'">tại đây</a>!</p>'
            send_email_notifile(order.customer.email, header, body)
            return HttpResponse(1)            

        if state == 0:
            if order_detail.first().state != '4':
                return HttpResponse('Đơn hàng bị từ chối trạng thái thất bại')
            # Khoong cho phep cap nhat so luong tin ! Do merchant huy don hang
            #for item in order_detail:
            order_detail.update(state=0, canceler_id=request.session.get('user')['id'])
            header = 'Đơn hàng bạn đã bị hủy vào lúc '+ str(datetime.now()) +' !'
            body = '<p>Vui lòng đánh giá người bán của chúng tôi <a href="/shop/'+ str(request.session.get('user')['id']) +'">tại đây</a>!</p>'
            send_email_notifile(order.customer.email, header, body)
            return HttpResponse(1)

        if state == 3:
            if order_detail.first().state != '2':
                return HttpResponse('Đơn hàng bị từ chối trạng thái gói hàng')
            order_detail.update(state=3)
            header = 'Đơn hàng bạn đang được đóng gói vào lúc '+ str(datetime.now()) +' !'
            body = '<p>Vui lòng đánh giá người bán của chúng tôi <a href="/shop/'+ str(request.session.get('user')['id']) +'">tại đây</a>!</p>'
            send_email_notifile(order.customer.email, header, body)
            return HttpResponse(1)  

        if state == 4:
            if order_detail.first().state != '3':
                return HttpResponse('Đơn hàng bị từ chối trạng thái vận chuyển')
            order_detail.update(state=4)
            header = 'Đơn hàng bạn đang được vận chuyển vào lúc '+ str(datetime.now()) +' !'
            body = '<p>Vui lòng đánh giá người bán của chúng tôi <a href="/shop/'+ str(request.session.get('user')['id']) +'">tại đây</a>!</p>'
            send_email_notifile(order.customer.email, header, body)
            return HttpResponse(1)  
    return HttpResponse('Xảy ra lỗi!')  


def order(request, id_order):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if Order_Detail.objects.filter(order_id=id_order, merchant_id=request.session.get('user')['id']).exists() == False:
            return HttpResponse('Đơn hàng không tồn tại!')
        order = Order.objects.get(pk=id_order).__dict__
        customer = Account.objects.get(pk=order['customer_id'])
        order['name_customer'] = customer.name
        rating_count = Rating_Customer.objects.filter(customer_id=order['customer_id']).count()
        rating_ponit = Rating_Customer.objects.filter(customer_id=order['customer_id']).aggregate(Sum('num_of_star'))['num_of_star__sum']
        if rating_ponit == None:
            rating_ponit = 0
        order['rating_count'] = rating_count
        order['rating_point'] = rating_ponit
        del order['_state']
        order_detail = Order_Detail.objects.filter(order_id=id_order, merchant_id=request.session.get('user')['id']).exclude(state__in = [0, 1])
        if order_detail.count() == 0:
            order['rate_cus'] = True
        else:
            order['rate_cus'] = False
        
        if Rating_Customer.objects.filter(merchant_id=request.session.get('user')['id'], customer_id=customer.id).exists() == True:
            order['value_rating'] = Rating_Customer.objects.filter(merchant_id=request.session.get('user')['id'], customer_id=customer.id).first().num_of_star
            order['disable_rating'] = True
        else:
            order['disable_rating']  = False
        state_now = -1
        for item in order_detail:
            state_now = item.state
            break
        order['state_now'] = state_now
        return HttpResponse(json.dumps(order, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")


def orders_detail(request, id_order):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        list_orders_detail = []
        order_detail_all = Order_Detail.objects.filter(order_id=id_order, merchant_id=request.session.get('user')['id'])
        for item in order_detail_all:
            order_item = []
            product_orgin_id = Link_Type.objects.get(product_id_id=item.product_id).parent_product
            product = Product.objects.get(pk=product_orgin_id)
            image = Product_Image.objects.filter(product_id_id=product_orgin_id, archive=False).order_by('image_id_id').first()
            order_item.append('<a href="/merchant/product/edit/'+ str(product_orgin_id) +'">'+ product.name +'</a>')
            order_item.append('<div class="tbl_thumb_product"><img src="/product' + image.image_id.image_link.url + '" /></div>')
            price = int(round((item.price * (100 - item.discount))/100, 0))
            order_item.append(str(price) + ' VND')
            order_item.append(str(item.quantity))
            if item.state == '1':
                order_item.append('<label class="label label-success">Thành công</label>')
            if item.state == '0':
                order_item.append('<label class="label label-danger">Hủy bỏ</label>')
            if item.state == '2':
                order_item.append('<label class="label label-info">Đặt hàng</label>')
            if item.state == '3':
                order_item.append('<label class="label label-warning">Đang gói hàng</label>')
            if item.state == '4':
                order_item.append('<label class="label label-default">Đang vận chuyển</label>') 
            list_orders_detail.append(order_item)
        return HttpResponse(json.dumps(list_orders_detail, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")

            
        


####3 END ORder


### Payment

def payments(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if request.GET.get('table') == 'true':
            list_payment = []
            payment_all = Purchase_Service.objects.filter(merchant_id_id=request.session.get('user')['id'])
            for item in payment_all:
                payment_item = []
                payment_item.append('<a>'+ item.purchase_name +'</a>')
                service = Service.objects.get(pk=item.service_id_id)
                payment_item.append('<a href="/merchant/purchase_service/'+ str(item.service_id_id) +'">'+ service.service_name +'</a>')
                payment_item.append(str(item.amount) + ' $')
                payment_item.append(item.success_at.replace(tzinfo=None))
                if item.state == 1:
                    payment_item.append('<label class="label label-success">Thanh toán thành công</label>')
                else:
                    payment_item.append('<label class="label label-danger">Thanh toán thất bại</label>')
                list_payment.append(payment_item)
            return HttpResponse(json.dumps(list_payment, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")
        return HttpResponse('No data')


@csrf_exempt
def rating_customer(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        customer_id = request.POST.get('customer_id')
        num_star = request.POST.get('num_star')
        customer = Account.objects.get(pk=customer_id)
        merchant = Account.objects.get(pk=request.session.get('user')['id'])

        if int(customer_id) == int(request.session.get('user')['id']):
            return HttpResponse('Không được phép thực hiện')

        if Rating_Customer.objects.filter(merchant_id=request.session.get('user')['id'], customer_id=customer_id).exists() == True:
            return HttpResponse('Bạn đã từng đánh giá người mua này!\n Đánh giá thất bại!')

        if Order_Detail.objects.filter(order_id=order_id, merchant_id=request.session.get('user')['id']).exclude(state__in = [0, 1]).count() > 0:
            return HttpResponse('Đơn hàng của bạn chưa hoàn thành!\nKhông được phép đánh giá!')

        if Order.objects.filter(pk=order_id, customer_id=customer_id).exists() == False:
            return HttpResponse('Không được phép thực hiện!')

        rating_cus = Rating_Customer.objects.create(
            customer =  customer,
            merchant =  merchant,
            num_of_star = num_star,
            confirm_bought = True,
        )
        header = 'Bạn được người bán '+ merchant.name_shop +' đánh giá!'
        body = '<h1>Bạn được đánh giá '+ num_star +' sao!</h1><p>Cám ơn bạn đã sử dụng dịch vụ của chúng tôi!</p><p>Đánh giá lại merchant <a href="/shop/'+ str(request.session.get('user')['id']) +'">tại đây</a>!</p>'
        send_email_notifile(customer.email, header, body)

        rating_count = Rating_Customer.objects.filter(customer_id=customer_id, is_activity=True).count()
        if rating_count == 0:
            header = 'Cảnh cáo!'
            body = '<h1>Tài khoản của bạn có nguy cơ bị khóa!\n Vui lòng liên hệ với chúng tôi để biết thêm thông tin!</h1>'
            send_email_notifile(customer.email, header, body)
        rating_ponit = Rating_Customer.objects.filter(customer_id=order['customer_id'], is_activity=True).aggregate(Sum('num_of_star'))['num_of_star__sum']
        if rating_ponit == None:
            rating_ponit = 0
        if (float(rating_point/rating_count) < 2):
            header = 'Cảnh cáo!'
            body = '<h1>Tài khoản của bạn có nguy cơ bị khóa!\n Vui lòng liên hệ với chúng tôi để biết thêm thông tin!</h1>'
            send_email_notifile(customer.email, header, body)
        return HttpResponse(1)

        
def list_rating(request):
    if check_rule(request) == 0:
        return HttpResponse('Quyền truy cập bị từ chối')
    if request.method == 'GET':
        if request.GET.get('table') == 'true':
            rating_all = Rating.objects.filter(merchant_id=request.session.get('user')['id'])
            list_rating = []
            for item in rating_all:
                rating_item = []
                rating_item.append('<a>'+ item.customer.name +'</a>')
                rating_item.append(str(item.num_of_star))
                rating_item.append(item.comment)
                if item.confirm_bought == True:
                    rating_item.append('<label class="label label-success">Đã mua</label>')
                else:
                    rating_item.append('<label class="label label-warning">Chưa mua</label>')
                if item.is_activity == True:
                    rating_item.append('<label class="label label-info">Ẩn</label>')
                else:
                    rating_item.append('<lable class="label label-default">Hiển thị</lable>')
                list_rating.append(rating_item)
            return HttpResponse(json.dumps(list_rating, sort_keys=False, indent=1, cls=DjangoJSONEncoder), content_type="application/json")
        return HttpResponse(503)
    return HttpResponse(404)



def send_email_notifile(email, body, content):

    mail = Mail(
        'smtp.gmail.com', 
        port='465', 
        username='dinhtai018@gmail.com', 
        password='wcyfglkfcshkxoaa',
        use_ssl=True,
        use_tls=False,
        debug_level=False
    )
    msg = Message(body)
    msg.fromaddr = ("Website C2C", "dinhtai018@gmail.com")
    msg.to = email
    msg.body = body
    msg.html = content
    msg.reply_to = 'no-reply@gmail.com'
    msg.charset = 'utf-8'
    msg.extra_headers = {}
    msg.mail_options = []
    msg.rcpt_options = []
    mail.send(msg)