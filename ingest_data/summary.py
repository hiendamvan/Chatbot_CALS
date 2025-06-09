'''
Use LLM to summarize chunk ans table, use this summary for embedding 
'''
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_ollama import ChatOllama

def summarize():
    # Prompt
    prompt_text = """You are an assistant tasked with summarizing tables and text. \ 
    Give a concise summary of the table or text. Table or text chunk: {element} """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # model 
    #model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    # Initialize LLM
    llm = ChatOllama(
        model='qwen3:0.6b',
        temperature=0.7,
        num_predict=512,
    )

    summarize_chain = {"element": lambda x: x} | prompt | llm | StrOutputParser()

    text = '''2.	Thành tích đạt được của cá nhân: Nêu thành tích cá nhân trong việc thực hiện nhiệm vụ được giao (Kết quả đã đạt được về năng suất, chất lượng, hiệu quả thực hiện nhiệm vụ; các biện pháp, giải pháp công tác trong việc đổi mới công tác quản lý, sáng kiến kinh nghiệm, đề tài nghiên cứu khoa học; việc đổi mới công nghệ, ứng dụng khoa học, kỹ thuật vào thực tiễn; việc thực hiện đường lối, chủ trương của Đảng, chính sách và pháp luật của Nhà nước; công tác bồi dưỡng nâng cao trình đội chuyên môn, phẩm chất đạo đức; chăm lo đời sống cán bộ, nhân viên; vai trò của cá nhân trong công tác xây dựng Đảng, đoàn thể; công tác tham gia hoạt động xã hội, từ thiện...)
    Đối với cán bộ làm công tác quản lý nêu tóm tắt thành tích của đơn vị, riêng thủ trưởng đơn vị kinh doanh lập bảng thống kê so sánh các tiêu chí: giá trị tổng sản lượng, doanh thu, lợi nhuận, tỷ suất lợi nhuận, nộp ngân sách nhà nước, đầu tư tái sản xuất, thu nhập bình quân; các sáng kiến được áp dụng, giá trị làm lợi; phúc lợi xã hội...
    '''
    summary = summarize_chain.invoke(text)
    return summary
