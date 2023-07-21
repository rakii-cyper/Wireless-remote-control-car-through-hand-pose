from pyngrok import ngrok

ngrok.set_auth_token("21nuvssLi4IA8Z9lxlWOJIpKNql_6s9ovG1EaMEJQTMAjeJPU")
public_url = ngrok.connect("http://192.168.0.116:81")

print(public_url)
