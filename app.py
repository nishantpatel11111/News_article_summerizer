import gradio as gr
import google.generativeai as genai
from newspaper import Article
import markdown
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ✅ Setup Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Dummy login credentials
USERNAME = "admin"
PASSWORD = "1234"

# ✅ Summarize article function
def summarize_article(url, language):
    try:
        article = Article(url)
        article.download()
        article.parse()

        prompt = f"""Summarize the following article in {language} with sections:
        Headline, Summary, Key Events, and Conclusion.

        Article Text:
        {article.text}
        """

        response = model.generate_content(prompt)

        html = markdown.markdown(response.text)
        soup = BeautifulSoup(html, "html.parser")
        summary = soup.get_text()

        filename = "summarized_article.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(summary)

        return summary, filename

    except Exception as e:
        return f"❌ Error: {e}", None

# ✅ Gradio UI with login + language + scroll
with gr.Blocks() as demo:
    gr.Markdown("## 🔐 Login to Access Gemini Article Summarizer")

    login_msg = gr.Markdown("")

    with gr.Column(visible=True) as login_row:
        user_input = gr.Textbox(label="Username")
        pass_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")

    with gr.Column(visible=False) as main_app:
        url_input = gr.Textbox(label="📥 Paste Article URL")
        language_dropdown = gr.Dropdown(
            choices=["English", "Hindi", "Gujarati"],
            value="English",
            label="🌐 Select Language for Summary"
        )
        summarize_button = gr.Button("Summarize")
        summary_output = gr.Textbox(
            label="📄 Summarized Article",
            lines=20,
            interactive=False,
            show_copy_button=True
        )
        file_output = gr.File(label="⬇️ Download Summary File")

        summarize_button.click(
            fn=summarize_article,
            inputs=[url_input, language_dropdown],
            outputs=[summary_output, file_output]
        )

    def login(username, password):
        if username == USERNAME and password == PASSWORD:
            return "✅ Logged in successfully", gr.update(visible=False), gr.update(visible=True)
        else:
            return "❌ Invalid credentials", gr.update(visible=True), gr.update(visible=False)

    login_button.click(
        fn=login,
        inputs=[user_input, pass_input],
        outputs=[login_msg, login_row, main_app]
    )

# ✅ Run app on correct host and port for Render
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )
