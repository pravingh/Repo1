import gradio as gr
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import GenerativeModel
import socket
import gradio as gr
import time
import requests
import magika
import vertexai
m = magika.Magika()
class CodeHolder:
    code_index = []
    code_text = ""
code_holder = CodeHolder()

# Function that takes User Inputs and displays it on ChatUI
def query_message(history, txt):
    history += [(txt, None)]
    return history

# Function that takes User Inputs, generates Response and displays on Chat UI
def llm_response(history, text, img):
    multimodal_model = GenerativeModel("gemini-1.5-pro")

    if not img:
        response = multimodal_model.generate_content(text)
        history += [(None, response.text)]
        return history

def get_code(repo_url):
    get_code_app_url = "https://git-app-amrxegrfpa-uc.a.run.app/get_code"
    repo_dir = "/tmp/repo"

    # clone_repo(repo_url, repo_dir)
    # code_holder.code_index, code_holder.code_text = extract_code(repo_dir)
    http_response = requests.get(
        get_code_app_url, params={"repo_url": repo_url}, verify=False
    )

    if http_response.status_code != 200:
        print(
            f"Failed to download code: {http_response.text}",
            {http_response.status_code},
        )
        return "Failed to download code"
    else:
        code_holder.code_text = http_response.json()[1]
        code_holder.code_index = http_response.json()[0]
    return "Code downloaded Successfully"

def get_code(repo_url):
    get_code_app_url = "https://git-app-amrxegrfpa-uc.a.run.app/get_code"
    repo_dir = "/tmp/repo"
    # clone_repo(repo_url, repo_dir)
    # code_holder.code_index, code_holder.code_text = extract_code(repo_dir)
    http_response = requests.get(
        get_code_app_url, params={"repo_url": repo_url}, verify=False
    )

    if http_response.status_code != 200:
        print(
            f"Failed to download code: {http_response.text}",
            {http_response.status_code},
        )
        return "Failed to download code"
    else:
        code_holder.code_text = http_response.json()[1]
        code_holder.code_index = http_response.json()[0]
    return "Code downloaded Successfully"

def deploy_code(repo_url, instructions):
    get_code_app_url = "https://git-app-amrxegrfpa-uc.a.run.app/deploy_code"
    response = requests.post(
        get_code_app_url,
        json={"instructions": instructions, "repo_url": repo_url},
        verify=False,
    )

    if response.status_code != 200:
        print(f"Failed to deploy code: {response.text}", {response.status_code})
        return "Failed to deploy code"
    else:
        return "Code deployed Successfully"

def get_code_prompt(question):
    """Generates a prompt to a code related question."""

    prompt = f"""



    Questions: {question}







    Context:



    - The entire codebase is provided below.



    - Here is an index of all of the files in the codebase:



    



    {code_holder.code_index}



.



    - Then each of the files is concatenated together. You will find all of the code you need:



    



    {code_holder.code_text}











    Answer:



    """

    return prompt


def add_content(prompt, chatbot, file):

    if file and prompt:

        chatbot = chatbot + [(prompt, None), ((file,), None)]

    elif prompt and not file:

        chatbot += [(prompt, None)]

    elif file and not prompt:

        chatbot += [((file,), None)]

    else:

        raise gr.Error("Enter a valid prompt or a file")

    return chatbot


def call_llm(history, question):

    prompt = get_code_prompt(question)

    contents = [prompt]

    multimodal_model = GenerativeModel("gemini-1.5-pro")

    response = multimodal_model.generate_content(contents, stream=True)

    history[-1][-1] = ""

    for resp in response:

        history[-1][-1] += resp.text

        yield history


def generate_suggeessions():

    contents = [
        "You are a Developer interacting with a Repository, respond with 5 questions which can be asked to understand the code."
    ]

    multimodal_model = GenerativeModel("gemini-1.5-pro")

    response = multimodal_model.generate_content(contents, stream=True)

    final_resposne = ""

    for resp in response:

        final_resposne += resp.text

        yield final_resposne


def generate_suggeessions():

    contents = [
        "You are a Developer interacting with a Repository, respond with 5 questions which can be asked to understand the code."
    ]

    multimodal_model = GenerativeModel("gemini-1.5-pro")

    response = multimodal_model.generate_content(contents, stream=True)

    final_resposne = ""

    for resp in response:

        final_resposne += resp.text

        yield final_resposne


def generate_instructions(repo_url):

    question = """Application is required to deploy on google cloud run, \

    provide instructions to do it in a json format with key and value format

    1. Dockerfile

    2. gcloud instructions using gcloud build and deploy in an array with variables <PROJECT_ID> <SERVICE_NAME> etc.\

    use SERVICE_NAME as the name of image and allow unauthenticated access.

    3. Identify list of variables which are required to replace.

    Don't provide any additional instructions"""

    multimodal_model = GenerativeModel("gemini-1.5-pro")

    contents = get_code_prompt(question)

    response = multimodal_model.generate_content(contents, stream=False)

    final_resposne = response.text

    deploy_code(repo_url, response.text)

    return final_resposne


def my_app(creds, app_port_param):

    vertexai.init(project="gsh002", location="us-central1", credentials=creds)

    with gr.Blocks(theme='HaleyCH/HaleyCH_Theme') as demo:
        
        gr.Markdown(
        """
        # Repository Alchemist - Gemini AI Powered Code Navigator!

        """
        )

        with gr.Row(
            visible=True,
        ) as git_hub:

            git_repo_url = gr.Textbox(
                type="text",
                label="Provide your git Repository url",
                value="https://github.com/pravingh/GeminiSummit",
                lines=2  # Limit the visible lines in the Textbox
            )

            get_code_button = gr.Button("Get Code from Git Repository")
            message = gr.Label()

        with gr.Row(visible=True):
            
            with gr.Row():            
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        show_copy_button=True,
                        height=300,
                    )
                    
                    prompt = gr.Textbox(placeholder="write prompt")
                    file = gr.File(visible=False)

                with gr.Column(scale=2):
                    with gr.Tab("Developer"):
                        examples = gr.Examples(
                        examples=[
                            ["Write a Developer guide for new joinne"],
                            ["Provide a way to containerize the repository"],
                            ["Scan Code and provide potential defects."],
                        ],                            
                        inputs=[prompt],
                        )
                        
                        button = gr.Button(
                            "Dockerize and Deploy App using Gemini Generated gcloud commands"
                        )
                        instructions = gr.Markdown()
                        button.click(
                            fn=generate_instructions,
                            inputs=[git_repo_url],
                            outputs=[instructions],
                        )
                        gr.Markdown("## Instructions Generated by Gemini Pro 1.5")                    

                    with gr.Tab("DevOps"):
                        with gr.Row():
                            with gr.Column(scale=3):

                                examples = gr.Examples(
                                    examples=[
                                        ["Write a DevOps guide for new joinee"],
                                        ["Provide a way to containerize the repository"],
                                        ["Proide a way to generate gitlab ci/cd pipeline"],
                                    ],
                                    inputs=[prompt],
                                )
                                
                                gr.Button("Whatever we want to Display here....")

        prompt.submit(
            fn=add_content, inputs=[prompt, chatbot, file], outputs=[chatbot]
        ).success(fn=call_llm, inputs=[chatbot, prompt], outputs=[chatbot])

        get_code_button.click(
            get_code, inputs=[git_repo_url], outputs=[message], show_progress=True
        )

    print("Starting app at http://{0}:{1}".format(socket.gethostname(), app_port_param))

    demo.launch(server_name="0.0.0.0", server_port=app_port_param)
    return demo

my_app(creds=None, app_port_param=9002)
