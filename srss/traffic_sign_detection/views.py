from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from traffic_sign_detection.camera import VideoCamera
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="/accounts/login")
def detect_traffic_sign(request):
    return render(request,'traffic_sign_detection.html')

def gen(camera,request):
    while(True):
        frame=camera.get_frame(request)
        yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed1(request):
    return StreamingHttpResponse(gen(VideoCamera(),request),
                        content_type='multipart/x-mixed-replace; boundary=frame')

