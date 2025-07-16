import gradio as gr
from google import genai
from google.genai import types
from newspaper import Article
import markdown
from bs4 import BeautifulSoup

# ✅ Setup Gemini
client = genai.Client(api_key="Your Gemini Key")

# ✅ Dummy credentials (you can replace this with a secure method)
USERNAME = "admin"
PASSWORD = "1234"

# ✅ Function to summarize article
def summarize_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        prompt = f"""Summarize the article with sections: Headline, Summary, Key Events, and Conclusion.
        Article Text: {article.text}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="Summarize the article by dividing into sections: Headline, Summary, Key Events, Conclusion."
            ),
            contents=prompt
        )

        html = markdown.markdown(response.text)
        soup = BeautifulSoup(html, "html.parser")
        summary = soup.get_text()

        filename = "summarized_article.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(summary)

        return summary, filename

    except Exception as e:
        return f"❌ Error: {e}", None


# ✅ Login check function
with gr.Blocks() as demo:
    gr.Markdown("## 🔐 Login to Access Gemini Article Summarizer")

    login_msg = gr.Markdown("")

    # Use 'login_row' and 'main_app' as references
    with gr.Column(visible=True) as login_row:
        user_input = gr.Textbox(label="Username")
        pass_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")

    with gr.Column(visible=False) as main_app:
        url_input = gr.Textbox(label="📥 Paste Article URL")
        summarize_button = gr.Button("Summarize")
        summary_output = gr.Textbox(label="📄 Summarized Article", lines=15)
        file_output = gr.File(label="⬇️ Download Summary File")
        summarize_button.click(fn=summarize_article, inputs=url_input, outputs=[summary_output, file_output])

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

demo.launch(share=True)
