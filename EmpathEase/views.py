from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

openaiApiKey = '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'
openai.api_key = openaiApiKey

def summarize_messages(messages):
    summarizer = LsaSummarizer()
    parser = PlaintextParser.from_string(messages, Tokenizer("english"))
    summary = summarizer(parser.document, 1)  # Resumir a 1 oración
    return str(summary[0])

def remove_redundant_messages(messages):
    cleaned_messages = []
    previous_message = None

    for message in messages:
        if message["content"] != previous_message:
            cleaned_messages.append(message)
            previous_message = message["content"]

    return cleaned_messages

def askOpenai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    answer = response.choices[0].message.content.strip()
    return answer

# Create your views here.
def empathEase(request):
    user_id = request.user.id
    chats = Chat.objects.filter(user_id=user_id)
    
    messages = [
        {"role": "system", "content": "You are a virtual psychologist here to listen and provide support."}
    ]
    for chat in chats:
        messages.append({"role": "user", "content": chat.message})
        messages.append({"role": "assistant", "content": chat.response})

    messages = remove_redundant_messages(messages)  # Elimina mensajes redundantes
    messages_text = "\n".join([message["content"] for message in messages])
    summarized_messages = summarize_messages(messages_text)  # Resume los mensajes
    
    if request.method == 'POST':
        message = request.POST.get('message')
        messages.append({"role": "user", "content": message})
        
        response = askOpenai(messages)
        
        chat = Chat(user_id=user_id, message=message, response=response, created_at=timezone.now())
        chat.save()
        
        return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'empathEase.html', {'chats': chats, 'summarized_messages': summarized_messages})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('EmpathEase')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
    
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('EmpathEase')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')