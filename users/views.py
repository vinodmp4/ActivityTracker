from django.shortcuts import render, redirect
from .forms import NewCertificateType, NewCertificate
from login.models import Profile, OTP, Notification
from .models import certificate_type, certificate
from django.utils.html import format_html
from django.middleware import csrf
# Create your views here.


class guest_mentor:
    def __init__(self):
        self.fullname= "Unassigned"
        self.dept = "NA"
        self.email = "NA"
        self.mobno = "NA"

def sentNotification(userid, message):
    new_notification = Notification(owner=userid, text=message, viewed= False)
    new_notification.save()
        
def getmyNotifications(myid):
    output = "</table>"
    dataset = Notification.objects.filter(owner=myid)
    for index, data in enumerate(dataset):
        if not(data.viewed):
            output = "<tr><td>"+str(len(dataset)-index)+"</td><td>"+data.text+"</td><td>New</td></tr>" + output
            Notification.objects.filter(pk=data.id).update(viewed=True)
        else:
            output = "<tr><td>"+str(len(dataset)-index)+"</td><td>"+data.text+"</td><td>Viewed</td></tr>" + output
    output = '<table class="tablellist"><tr><th>Serial Number</th><th>Message</th><th>Status</th></tr>' + output
    return output

def get_profile(profile):
    return (profile.fullname, profile.regid, profile.acayear, profile.dept, profile.email, profile.mobno, profile.verified, profile.usertype)

def get_usertype(key):
    return {'ad':'Administrator', 'fa':'Faculty', 'st':'Student'}.get(key, 'Student')

def get_selected_cat(cat_dict):
    out = []
    for k in cat_dict.keys():
        scores = [];year_limit = []
        for l in cat_dict[k]:
            scores.append(int(l[1]))
            year_limit.append(int(l[2]))
        scores.sort(reverse=True)
        y_limit = min(year_limit)
        scores = scores[0:y_limit]
        temp_out = []
        for l in cat_dict[k]:
            if int(l[1]) in scores:
                temp_out.append(l[0])
        for t_o in temp_out[0:y_limit]:
            out.append(t_o)
    return out

def get_selected_score_index(all_scores):
    output = []
    for key in all_scores.keys():
        cat_dict = {}
        for i in all_scores[key]:
            if not(i[1] in cat_dict.keys()):cat_dict[i[1]] = []
            cat_dict[i[1]].append([i[0],i[2],i[3]])
        selected_index = get_selected_cat(cat_dict)
        for s in selected_index:
            if not(s in output):output.append(s)
    return output

def split_by_aca_year(user_certificates):
    aca_year = [1,2,3,4]; aca_year_data = {1:[[],[]],2:[[],[]],3:[[],[]],4:[[],[]]}
    if len(user_certificates)>0:
        for u_c in user_certificates:
            if (u_c.verified):
                ac_year = int((u_c.semester+1)/2)
                if not(ac_year in aca_year):aca_year.append(ac_year);aca_year_data[ac_year] = [[],[]]
                cat = certificate_type.objects.get(pk=u_c.doc_id)
                if u_c.hardcopy:aca_year_data[ac_year][0].append([cat.category,cat.title,u_c.doc_desc,cat.grade,cat.score,'Hardcopy',u_c.id])
                else:aca_year_data[ac_year][0].append([cat.category,cat.title,u_c.doc_desc,cat.grade,cat.score,u_c.doc_loc,u_c.id])
                aca_year_data[ac_year][1].append([u_c.id, cat.identifier, cat.score, cat.year_max])
    return aca_year_data

def split_stud_by_aca_year(data):
    output = {}
    for stud in data:
        if not(stud.acayear in list(output.keys())):output[stud.acayear]=[]
        stud_certs = certificate.objects.filter(owner_id=stud.user_id)
        stud_aca_year = split_by_aca_year(stud_certs)
        year_ids = []; year_data = {};score_finder_data = {};selected_scores = []
        for key in stud_aca_year.keys():
            year_ids.append(key)
            year_data[key] = stud_aca_year[key][0]
            score_finder_data[key] = stud_aca_year[key][1]
        if len(list(score_finder_data.keys()))>0:selected_scores = get_selected_score_index(score_finder_data)
        year_ids.sort()
        year_based_score = {}
        for yr in year_ids:
            user_year_score = 0
            for y in year_data[yr]:
                if y[6] in selected_scores:user_year_score += int(y[4])
            year_based_score[yr] = user_year_score
        output[stud.acayear].append([stud.fullname, stud.regid, stud.dept, stud.email, stud.mobno, year_based_score, stud.user_id])
    return output

def admin_home(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pass
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='ad'):return redirect("/")
        data = f"<table><tr><th>Full Name:</th><td>{pd[0]}</td></tr>\
                    <tr><th>ID:</th><td>{pd[1]}</td></tr>\
                    <tr><th>Academic/ Joining Year:</th><td>{pd[2]}</td></tr>\
                    <tr><th>Department:</th><td>{pd[3]}</td></tr>\
                    <tr><th>E-Mail:</th><td>{pd[4]}</td></tr>\
                    <tr><th>Mobile:</th><td>{pd[5]}</td></tr>\
                    <tr><th>User Type:</th><td>{get_usertype(pd[-1])}</td></tr></table>"
        return render(request, 'users/admin_profile.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def admin_verify(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            req_origin = request.POST.getlist('button-action')
            if ('verify' in req_origin):
                prof_list = request.POST.getlist('boxes')
                unverify = request.POST.getlist('unverify')
                for pro in prof_list:
                    if len(unverify)>0:
                        Profile.objects.filter(user=pro).update(verified=False)
                    else:
                        Profile.objects.filter(user=pro).update(verified=True)
        # End of updation --------------------
        all_profile = Profile.objects.all()
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='ad'):return redirect("/")
        csrf_token = csrf.get_token(request)
        all_user_data = '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'
        all_user_data += '<table class="tablellist"><tr><th>Full Name</th><th>Registration ID</th><th>Academic Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th><th>User Type</th><th>Verified</th></tr>'
        for prof_ in all_profile:
            if prof_.verify_applied and not(prof_.id == profile.id):
                all_user_data += f"<tr><td>{prof_.fullname}</td><td>{prof_.regid}</td><td>{prof_.acayear}</td><td>{prof_.dept}</td><td>{prof_.email}</td><td>{prof_.mobno}</td><td>{get_usertype(prof_.usertype)}</td>"
                if prof_.verified:
                    all_user_data += '<td><div class="form-check"><input class="form-check-input" type="checkbox" checked="checked" value="'+str(prof_.user_id)+'" name="boxes"></div></td>'
                else:
                    all_user_data += '<td><div class="form-check"><input class="form-check-input" type="checkbox" value="'+str(prof_.user_id)+'" name="boxes"></div></td>'
                all_user_data += "</tr>"
        all_user_data += '<tr><td>Unverify selected</td><td><div class="form-check"><input class="form-check-input" type="checkbox" value="'+str(1)+'" name="unverify"></div></td></tr></table></br></br><button class="btn btn-secondary" name="button-action" value="verify" type="submit">Save</button></form>'
        return render(request, 'users/admin_verify.html', {"uname":pd[0], "data":format_html(all_user_data)})
    else:
        return redirect("/login")

def admin_certificates(request):
    if request.user.is_authenticated:
        editable = False
        if request.method == "POST":
            edit_cert = request.POST.getlist('edit_cert')
            if len(edit_cert)>0:editable = True
            update_cert = request.POST.getlist('update_cert')
            if len(update_cert)>0:
                id_ = update_cert[0]
                category = request.POST.getlist('category')[0]
                identifier = request.POST.getlist('identifier')[0]
                title = request.POST.getlist('title')[0]
                grade = request.POST.getlist('grade')[0]
                score = request.POST.getlist('score')[0]
                year_max = request.POST.getlist('year_max')[0]
                certificate_type.objects.filter(id=id_).update(category=category)
                certificate_type.objects.filter(id=id_).update(identifier=identifier)
                certificate_type.objects.filter(id=id_).update(title=title)
                certificate_type.objects.filter(id=id_).update(grade=grade)
                certificate_type.objects.filter(id=id_).update(score=score)
                certificate_type.objects.filter(id=id_).update(year_max=year_max)
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='ad'):return redirect("/")
        csrf_token = csrf.get_token(request)
        form = NewCertificateType(request.POST)
        if form.is_valid():
            category = form.cleaned_data.get('document_category')
            identifier = form.cleaned_data.get('document_identifier')
            title = form.cleaned_data.get('document_title')
            grade = form.cleaned_data.get('document_grade')
            score = form.cleaned_data.get('document_score')
            year_max = form.cleaned_data.get('year_maximum')
            user = form.save()
            certificate_type.objects.filter(id=user.id).update(category=category)
            certificate_type.objects.filter(id=user.id).update(identifier=identifier)
            certificate_type.objects.filter(id=user.id).update(title=title)
            certificate_type.objects.filter(id=user.id).update(grade=grade)
            certificate_type.objects.filter(id=user.id).update(score=score)
            certificate_type.objects.filter(id=user.id).update(year_max=year_max)
        all_certificates = certificate_type.objects.all()
        all_cert_data = ""
        if len(all_certificates)>0:
            all_cert_data += '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'
            all_cert_data += '<table class="tablellist"><tr><th>Category</th><th>Identifier</th><th>Title</th><th>Grade</th><th>Score</th><th>Year Limit</th><th>Action</th></tr>'
            for cert in all_certificates:
                if editable: # 
                    if str(cert.id) in edit_cert:
                        all_cert_data += '<tr><td><input type="text" name="category" value="'+str(cert.category)+'"></td><td><input type="text" name="identifier" value="'+str(cert.identifier)+'"></td><td><input type="text" name="title" value="'+str(cert.title)+'"></td>'
                        all_cert_data += '<td><input type="text" name="grade" value="'+str(cert.grade)+'"></td><td><input type="text" name="score" value="'+str(cert.score)+'"></td><td><input type="text" name="year_max" value="'+str(cert.year_max)+'"></td>'
                        all_cert_data += '<td><button name="update_cert" value="'+str(cert.id)+'" type="submit">Update</button></td></tr>'
                    else:all_cert_data += f'<tr><td>{cert.category}</td><td>{cert.identifier}</td><td>{cert.title}</td><td>{cert.grade}</td><td>{cert.score}</td><td>{cert.year_max}</td><td><button name="edit_cert" value="{cert.id}" type="submit">Edit</button></td></tr>'
                else:all_cert_data += f'<tr><td>{cert.category}</td><td>{cert.identifier}</td><td>{cert.title}</td><td>{cert.grade}</td><td>{cert.score}</td><td>{cert.year_max}</td><td><button name="edit_cert" value="{cert.id}" type="submit">Edit</button></td></tr>'
            all_cert_data += '</table></form>'
        return render(request, 'users/admin_certificates.html', {"uname":pd[0],"new_data":form,'data':format_html(all_cert_data)})
    else:
        return redirect("/login")

def admin_OTP(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        OTPS = OTP.objects.all()
        this_otps = []
        OTPDATA = "No Requests"
        temp_html = 'OTP Requests </br><table class="tablellist"><tr><th>Full Name</th><th>Registration ID</th><th>Joining Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th><th>OTP</th></tr>'
        temp_flag = False
        for OTP_ in OTPS:
            otp_owner = Profile.objects.filter(pk = OTP_.owner)
            if otp_owner.values('usertype')[0]['usertype']=='fa':
            	temp_flag = True
            	this_otps.append([otp_owner.values('fullname')[0]['fullname'], otp_owner.values('regid')[0]['regid'], str(otp_owner.values('acayear')[0]['acayear']),
                                  otp_owner.values('dept')[0]['dept'], otp_owner.values('email')[0]['email'], otp_owner.values('mobno')[0]['mobno'], OTP_.text])
        if temp_flag:
            OTPDATA = temp_html
            for otp_ in this_otps:
                OTPDATA += "<tr><td>"+"</td><td>".join(otp_)+"</td></tr>"
            OTPDATA += "</table></br></br>"
        return render(request, 'users/admin_faculty.html', {"uname":pd[0], "data":format_html(OTPDATA)})
    else:
        return redirect("/login")

def admin_faculty(request):
    fac_list = []
    if request.user.is_authenticated:
        if request.method == "POST":
            req_origin = request.POST.getlist('button-action')
            if ('faculty' in req_origin):fac_list = request.POST.getlist('selected_faculty')
            req_assign = request.POST.getlist('button-assign')
            if ('faculty' in req_assign):
                fac_list = request.POST.getlist('selected_faculty')
                studs = request.POST.getlist('stud_assign')
                for stu in studs:
                    Profile.objects.filter(user_id=int(stu)).update(mentor=int(fac_list[0]))
            req_unassign = request.POST.getlist('button-unassign')
            if ('faculty' in req_unassign):
                fac_list = request.POST.getlist('selected_faculty')
                studs = request.POST.getlist('stud_unassign')
                for stu in studs:
                    Profile.objects.filter(user_id=int(stu)).update(mentor=-1)
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='ad'):return redirect("/")
        csrf_token = csrf.get_token(request)
        faculty_list = Profile.objects.filter(usertype='fa')
        if len(faculty_list)>0:
            faculty = '<a href="/user/admin/faculty">Check Another Faculty</a></br><form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'
            faculty += '<table class="tablellist"><tr><th>Full Name</th><th>Registration ID</th><th>Joining Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th><th>Select</th></tr>'
            if len(fac_list)<=0:
                for fac in faculty_list:
                    fa =  get_profile(fac)
                    faculty += f"<tr><td>{fa[0]}</td><td>{fa[1]}</td><td>{fa[2]}</td><td>{fa[3]}</td><td>{fa[4]}</td><td>{fa[5]}</td><td><div><input type="+'"radio" value="'+str(fac.user_id)+'" name="selected_faculty"></div></td></tr>'
                faculty += '</table></br>'
            else:
                for fac in faculty_list:
                    if str(fac.user_id) in fac_list:
                        faculty += f"<tr><td>{fac.fullname}</td><td>{fac.regid}</td><td>{fac.acayear}</td><td>{fac.dept}</td><td>{fac.email}</td><td>{fac.mobno}</td><td>Selected</td></tr>"
                faculty += '</table></br>'
                stud_list = Profile.objects.filter(mentor=int(fac_list[0]))
                unlisted_stud_list = Profile.objects.filter(mentor=-1, usertype='st')
                if len(stud_list)>0:
                    faculty += "<table><caption></br></br>Assigned Students</caption><tr><th>Full Name</th><th>Registration ID</th><th>Joining Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th></tr>"
                    for stud in stud_list:
                        st = get_profile(stud)
                        if st[-1] == 'st':
                            faculty += f"<tr><td>{st[0]}</td><td>{st[1]}</td><td>{st[2]}</td><td>{st[3]}</td><td>{st[4]}</td><td>{st[5]}</td>"
                            faculty += '<td><div><input type="checkbox" value="'+str(stud.user_id)+'" name="stud_unassign"></div></td></tr>'
                    faculty += "</table>"
                    faculty += '<button class="btn btn-secondary" name="button-unassign" value="faculty" type="submit">Unassign</button>'
                if len(unlisted_stud_list)>0:
                    faculty += "<table><caption></br></br>Unassigned Students</caption><tr><th>Full Name</th><th>Registration ID</th><th>Joining Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th></tr>"
                    for stud in unlisted_stud_list:
                        st = get_profile(stud)
                        if st[-1] == 'st':
                            faculty += f"<tr><td>{st[0]}</td><td>{st[1]}</td><td>{st[2]}</td><td>{st[3]}</td><td>{st[4]}</td><td>{st[5]}</td>"
                            faculty += '<td><div><input type="checkbox" value="'+str(stud.user_id)+'" name="stud_assign"></div></td></tr>'
                    faculty += "</table>"
                    faculty += '<button class="btn btn-secondary" name="button-assign" value="faculty" type="submit">Assign</button>'
            
            if len(fac_list)<=0:
                faculty += '<button class="btn btn-secondary" name="button-action" value="faculty" type="submit">Select</button>'
            else:
                faculty += '<input type="hidden" name="selected_faculty" value="'+fac_list[0]+'">'
            faculty += '</form>'
        else:faculty = "<div>No Faculy to Show :(</div>"
        return render(request, 'users/admin_faculty.html', {"uname":pd[0], "data":format_html(faculty)})
    else:
        return redirect("/login")


def faculty_home(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pass
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='fa'):return redirect("/")
        data = f"<table><tr><th>Full Name:</th><td>{pd[0]}</td></tr>\
                    <tr><th>ID:</th><td>{pd[1]}</td></tr>\
                    <tr><th>Academic/ Joining Year:</th><td>{pd[2]}</td></tr>\
                    <tr><th>Department:</th><td>{pd[3]}</td></tr>\
                    <tr><th>E-Mail:</th><td>{pd[4]}</td></tr>\
                    <tr><th>Mobile:</th><td>{pd[5]}</td></tr>\
                    <tr><th>User Type:</th><td>{get_usertype(pd[-1])}</td></tr></table>"
        tabs = ["Profile", "Dashboard", "Students"]
        return render(request, 'users/faculty_profile.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def faculty_OTP(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        OTPS = OTP.objects.all()
        this_otps = []
        OTPDATA = "No Requests"
        temp_html = 'OTP Requests </br><table class="tablellist"><tr><th>Full Name</th><th>Registration ID</th><th>Joining Year</th><th>Department</th><th>E Mail</th><th>Mobile Number</th><th>OTP</th></tr>'
        temp_flag = False
        for OTP_ in OTPS:
            otp_owner = Profile.objects.filter(pk = OTP_.owner)
            if ((otp_owner.values('usertype')[0]['usertype']=='st') and (otp_owner.values('mentor')[0]['mentor']==profile.user_id)):
            	temp_flag = True
            	this_otps.append([otp_owner.values('fullname')[0]['fullname'], otp_owner.values('regid')[0]['regid'], str(otp_owner.values('acayear')[0]['acayear']),
                                  otp_owner.values('dept')[0]['dept'], otp_owner.values('email')[0]['email'], otp_owner.values('mobno')[0]['mobno'], OTP_.text])
        if temp_flag:
            OTPDATA = temp_html
            for otp_ in this_otps:
                OTPDATA += "<tr><td>"+"</td><td>".join(otp_)+"</td></tr>"
            OTPDATA += "</table></br></br>"
        return render(request, 'users/faculty_dashboard.html', {"uname":pd[0], "data":format_html(OTPDATA)})
    else:
        return redirect("/login")

def faculty_dashboard(request):
    if request.user.is_authenticated:
        view_profile = False
        if request.method == "POST":
            selected_students = request.POST.getlist('selected_student')
            if len(selected_students)>0:
                view_profile = True
                s_c = selected_students[0]
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='fa'):return redirect("/")
        if not(view_profile):
            data = '</br></br>No assigned students'
            stud_list = Profile.objects.filter(mentor=profile.user_id, usertype='st')
            score_by_student_by_year = split_stud_by_aca_year(stud_list)
            if len(score_by_student_by_year.keys())>0:
                csrf_token = csrf.get_token(request)
                data = '<form id="selectstudentform" action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'
                for yr in score_by_student_by_year.keys():
                    year_d = int(yr) # eg. 2018
                    data += f'<div id="switch{yr}" style="margin:20px;border:1px gray solid; padding:10px; text-align:left;width:50%;font-weight:bold;font-size:20px;" onclick=\'toggle({yr},"Batch {year_d} - {year_d+4}")\'>&#11166; &emsp;Batch {year_d} - {year_d+4}</div>'
                    data += f'<section id="{yr}" hidden="hidden"><table><tr><th>Full Name</th><th>Registration ID</th><th>Department</th><th>E Mail</th><th>Mobile Number</th><th>Year 1 Score</th><th>Year 2 Score</th><th>Year 3 Score</th><th>Year 4 Score</th><th>Select</th></tr>'
                    for stud_data in score_by_student_by_year[yr]:
                        data += f'<tr><td>{stud_data[0]}</td><td>{stud_data[1]}</td><td>{stud_data[2]}</td><td>{stud_data[3]}</td><td>{stud_data[4]}</td><td>{stud_data[5][1]}</td><td>{stud_data[5][2]}</td><td>{stud_data[5][3]}</td><td>{stud_data[5][4]}</td><td><input type="radio" onChange="submitform()" name="selected_student" value="{stud_data[6]}"></td></tr>'
                    data += "</table></section>"
                data += '</form>'
        else:
            stud_prof = Profile.objects.get(user=s_c)
            if stud_prof.mentor == profile.user_id:
                data = f'<h3>Showing report of {stud_prof.fullname}</h3></br>'
                user_certificates = certificate.objects.filter(owner_id=s_c)
                temp_data = split_by_aca_year(user_certificates)
                year_ids = []; year_data = {};score_finder_data = {};selected_scores = []
                for key in temp_data.keys():
                    year_ids.append(key)
                    year_data[key] = temp_data[key][0]
                    score_finder_data[key] = temp_data[key][1]
                if len(list(score_finder_data.keys()))>0:selected_scores = get_selected_score_index(score_finder_data)
                if len(year_ids)>0:
                    year_ids.sort()
                    year_based_score = {}
                    for yr in year_ids:
                        user_year_score = 0
                        for y in year_data[yr]:
                            if y[6] in selected_scores:user_year_score += int(y[4])
                        year_based_score[yr] = user_year_score
                    data += '<table><tr><th>Academic Year</th>'
                    for yr in year_ids:
                        data += f'<th>{profile.acayear + (yr-1)} - {profile.acayear + yr}</th>'
                    data += '</tr><tr><th>Score</th>'
                    for yr in year_ids:
                        data += f'<td>{year_based_score[yr]}</td>'
                    data += '</tr></table>'
                    year_ids.sort(reverse=True)
                    for yr in year_ids:
                        data += f'<div id="switch{yr}" style="margin:20px;border:1px gray solid; padding:10px; text-align:left;width:50%;font-weight:bold;font-size:20px;" onclick=\'toggle({yr},"Academic Year {profile.acayear + (yr-1)} - {profile.acayear + yr}")\'>&#11166; &emsp;Academic Year {profile.acayear + (yr-1)} - {profile.acayear + yr}</div>'
                        data += f'<div  style="text-align:left;width:50%;font-weight:bold;">Total score: {year_based_score[yr]}</div>'
                        data += f'<section id="{yr}" hidden="hidden"><table><tr><th>Category</th><th>Title</th><th>Description</th><th>Grade</th><th>Score</th><th>Proof</th><th>Selected for Score</th></tr>'
                        for y in year_data[yr]:
                            selec = "&#10007;"
                            if y[6] in selected_scores:selec = "&#9989;"
                            if y[5]=='Hardcopy':data += f'<tr><td>{y[0]}</td><td>{y[1]}</td><td>{y[2]}</td><td>{y[3]}</td><td>{y[4]}</td><td>{y[5]}</td><td>{selec}</td></tr>'
                            else:data += f'<tr><td>{y[0]}</td><td>{y[1]}</td><td>{y[2]}</td><td>{y[3]}</td><td>{y[4]}</td><td><a href="../../{y[5]}">View File</a></td><td>{selec}</td></tr>'
                        data += "</table></section>"
            else:return redirect("/user/faculty/dashboard")
        return render(request, 'users/faculty_dashboard.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def faculty_verify(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if request.method == "POST":
            verify_cert = request.POST.getlist('verified_certificates')
            if len(verify_cert)>0:
                for v_c in verify_cert:
                    certificate.objects.filter(id=int(v_c)).update(verified=True)
                    this_cert = certificate.objects.filter(id=int(v_c))
                    user_index = this_cert.values('owner_id')[0]['owner_id']
                    sentNotification(user_index, 'Your '+this_cert.values('doc_desc')[0]['doc_desc']+' certificate has been verified by '+pd[0])
            rejected_cert = request.POST.getlist('rejected_certificates')
            if len(rejected_cert)>0:
                for r_c in rejected_cert:
                    certificate.objects.filter(id=int(r_c)).update(rejected=True)
                    this_cert = certificate.objects.filter(id=int(r_c))
                    user_index = this_cert.values('owner_id')[0]['owner_id']
                    sentNotification(user_index, 'Your '+this_cert.values('doc_desc')[0]['doc_desc']+' certificate has been rejected by '+pd[0])
        # End of updation --------------------
        if not(pd[-1]=='fa'):return redirect("/")
        stud_list = Profile.objects.filter(mentor=profile.user_id, usertype='st')
        stud_ids = [stud.user_id for stud in stud_list]
        unverified_certificates = [];data = '</br></br>Nothing to Verify'
        for st_id in stud_ids:
            user_certificates = certificate.objects.filter(owner_id=st_id)
            for u_c in user_certificates:
                if not(u_c.verified):unverified_certificates.append(u_c)
        if len(unverified_certificates)>0:
            remove_index = []
            for ind, u_c in enumerate(unverified_certificates):
                if u_c.rejected:remove_index.append(ind)
            remove_index.sort(reverse=True)
            for ind in remove_index:
                temp_val = unverified_certificates.pop(ind)
        if len(unverified_certificates)>0:
            csrf_token = csrf.get_token(request)
            data = '<form action="" method="POST"><input type="hidden" name="csrfmiddlewaretoken" value="'+csrf_token+'">'
            data += '<table class="tablellist"><tr><th>Submitted by</th><th>Registration ID</th><th>Certificate Category</th><th>Certificate Title</th><th>Certificate Description</th><th>Proof</th><th>Verify</th><th>Rejected</th></tr>'
            for u_c in unverified_certificates:
                stud_prof = Profile.objects.get(user=u_c.owner_id)
                cat = certificate_type.objects.get(pk=u_c.doc_id)
                if (u_c.hardcopy):data += f'<tr><td>{stud_prof.fullname}</td><td>{stud_prof.regid}</td><td>{cat.category}</td><td>{cat.title}</td><td>{u_c.doc_desc}</td><td>Hardcopy Submitted</td>'
                else:data += f'<tr><td>{stud_prof.fullname}</td><td>{stud_prof.regid}</td><td>{cat.category}</td><td>{cat.title}</td><td>{u_c.doc_desc}</td><td><a href="../../{u_c.doc_loc}">View File</a></td>'
                data += f'<td><div><input type="checkbox" value="{u_c.id}" name="verified_certificates"></div></td><td><div><input type="checkbox" value="{u_c.id}" name="rejected_certificates"></div></td></tr>'
            data += '</table></br></br><button class="btn btn-secondary" name="button-action" value="verify" type="submit">Save</button></form>'
        return render(request, 'users/faculty_verify.html',{"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def student_home(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pass
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='st'):return redirect("/")
        data = f"<table><tr><th>Full Name:</th><td>{pd[0]}</td></tr>\
                    <tr><th>ID:</th><td>{pd[1]}</td></tr>\
                    <tr><th>Academic/ Joining Year:</th><td>{pd[2]}</td></tr>\
                    <tr><th>Department:</th><td>{pd[3]}</td></tr>\
                    <tr><th>E-Mail:</th><td>{pd[4]}</td></tr>\
                    <tr><th>Mobile:</th><td>{pd[5]}</td></tr>\
                    <tr><th>User Type:</th><td>{get_usertype(pd[-1])}</td></tr></table>"
        return render(request, 'users/student_profile.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def student_notifications(request):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        notifications = getmyNotifications(request.user.id)
        data = notifications
        return render(request, 'users/student_dashboard.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def student_dashboard(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pass
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        if not(pd[-1]=='st'):return redirect("/")
        try:mentor = Profile.objects.get(user_id=profile.mentor)
        except Exception as e:mentor = guest_mentor()
        data = f"<table><tr><th>Mentor</th><th>Department</th><th>Email</th><th>Phone</th></tr><tr><td>{mentor.fullname}</td><td>{mentor.dept}</td><td>{mentor.email}</td><td>{mentor.mobno}</td></tr></table>"
        user_certificates = certificate.objects.filter(owner_id=request.user.id)
        temp_data = split_by_aca_year(user_certificates)
        year_ids = []; year_data = {};score_finder_data = {};selected_scores = []
        for key in temp_data.keys():
            year_ids.append(key)
            year_data[key] = temp_data[key][0]
            score_finder_data[key] = temp_data[key][1]
        if len(list(score_finder_data.keys()))>0:selected_scores = get_selected_score_index(score_finder_data)
        if len(year_ids)>0:
            year_ids.sort()
            year_based_score = {}
            for yr in year_ids:
                user_year_score = 0
                for y in year_data[yr]:
                    if y[6] in selected_scores:user_year_score += int(y[4])
                year_based_score[yr] = user_year_score
            data += '<table><tr><th>Academic Year</th>'
            for yr in year_ids:
                data += f'<th>{profile.acayear + (yr-1)} - {profile.acayear + yr}</th>'
            data += '</tr><tr><th>Score</th>'
            for yr in year_ids:
                data += f'<td>{year_based_score[yr]}</td>'
            data += '</tr></table>'
            year_ids.sort(reverse=True)
            for yr in year_ids:
                data += f'<div id="switch{yr}" style="margin:20px;border:1px gray solid; padding:10px; text-align:left;width:50%;font-weight:bold;font-size:20px;" onclick=\'toggle({yr},"Academic Year {profile.acayear + (yr-1)} - {profile.acayear + yr}")\'>&#11166; &emsp;Academic Year {profile.acayear + (yr-1)} - {profile.acayear + yr}</div>'
                data += f'<div  style="text-align:left;width:50%;font-weight:bold;">Total score: {year_based_score[yr]}</div>'
                data += f'<section id="{yr}" hidden="hidden"><table><tr><th>Category</th><th>Title</th><th>Description</th><th>Grade</th><th>Score</th><th>Proof</th><th>Selected for Score</th></tr>'
                for y in year_data[yr]:
                    selec = "&#10007;"
                    if y[6] in selected_scores:selec = "&#9989;"
                    if y[5]=='Hardcopy':data += f'<tr><td>{y[0]}</td><td>{y[1]}</td><td>{y[2]}</td><td>{y[3]}</td><td>{y[4]}</td><td>{y[5]}</td><td>{selec}</td></tr>'
                    else:data += f'<tr><td>{y[0]}</td><td>{y[1]}</td><td>{y[2]}</td><td>{y[3]}</td><td>{y[4]}</td><td><a href="../../{y[5]}">View File</a></td><td>{selec}</td></tr>'
                data += "</table></section>"
        return render(request, 'users/student_dashboard.html', {"uname":pd[0], 'data':format_html(data)})
    else:
        return redirect("/login")

def student_newcertificate(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            file_keys = list(request.FILES.keys())
            for f_k in file_keys:
                try:
                    this_cert = certificate.objects.get(pk=int(f_k))
                    this_file = request.FILES[f_k]
                    filename = 'media/'+str(this_cert.owner_id)+'_'+str(this_cert.doc_id)+'_'+str(f_k)+'.'+this_file.name.split('.')[-1]
                    with open(filename, 'wb+') as destination:
                        for chunk in this_file.chunks():
                            destination.write(chunk)
                    certificate.objects.filter(id=int(f_k)).update(doc_loc=filename)
                except Exception as e:pass
            pass
        # End of updation --------------------
        profile = Profile.objects.get(user=request.user)
        pd = get_profile(profile)
        csrf_token = csrf.get_token(request)
        if not(pd[-1]=='st'):return redirect("/")
        form = NewCertificate(request.POST)
        if form.is_valid():
            document_id = form.cleaned_data.get('document_id').id
            document_description = form.cleaned_data.get('document_description')
            semester = form.cleaned_data.get('semester')
            year = form.cleaned_data.get('year')
            hardcopy = form.cleaned_data.get('hardcopy',False)
            user = form.save()
            certificate.objects.filter(id=user.id).update(owner_id=request.user.id)
            certificate.objects.filter(id=user.id).update(doc_id=document_id)
            certificate.objects.filter(id=user.id).update(doc_desc=document_description)
            certificate.objects.filter(id=user.id).update(semester=semester)
            certificate.objects.filter(id=user.id).update(year=year)
            certificate.objects.filter(id=user.id).update(hardcopy=hardcopy)
        user_certificates = certificate.objects.filter(owner_id=request.user.id)
        data = ""
        if len(user_certificates)>0:
            data = f'<form method="POST" enctype="multipart/form-data"><input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}"><table><tr><th>Category</th><th>Title</th><th>Description</th><th>Grade</th><th>Score</th><th>Year</th><th>Proof</th><th>Verified</th></tr>'
            for u_c in user_certificates:
                if not(u_c.verified):
                    cat = certificate_type.objects.get(pk=u_c.doc_id)
                    if u_c.hardcopy:data += f'<tr><td>{cat.category}</td><td>{cat.title}</td><td>{u_c.doc_desc}</td><td>{cat.grade}</td><td>{cat.score}</td><td>{u_c.year}</td><td>Hardcopy Submitted</td><td>{u_c.verified}</td></tr>'
                    else:
                        if len(u_c.doc_loc)>1:
                            data += f'<tr><td>{cat.category}</td><td>{cat.title}</td><td>{u_c.doc_desc}</td><td>{cat.grade}</td><td>{cat.score}</td><td>{u_c.year}</td><td><a href="../../{u_c.doc_loc}">View File</a></td><td>{u_c.verified}</td></tr>'
                        else:data += f'<tr><td>{cat.category}</td><td>{cat.title}</td><td>{u_c.doc_desc}</td><td>{cat.grade}</td><td>{cat.score}</td><td>{u_c.year}</td><td><input type="file" name="{u_c.id}"></td><td>{u_c.verified}</td></tr>'
            data += '</table><button type="submit">Upload and Save</button></form>'
        return render(request, 'users/student_newcertificate.html', {"uname":pd[0], "new_data":form, 'data':format_html(data)})
    else:
        return redirect("/login")

