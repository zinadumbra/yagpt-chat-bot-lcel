# создаем простое streamlit приложение для чата с YaGPT через веб, используя публичный API

import streamlit as st
import os
from dotenv import load_dotenv


# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
from streamlit_chat import message

from yandex_chain import YandexLLM
from langchain_community.chat_models import ChatYandexGPT

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# для добавления памяти
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from operator import itemgetter
from langchain.memory import ConversationBufferMemory

# это основная функция, которая запускает приложение streamlit
def main():
    # Загрузка логотипа компании
    logo_image = './images/logo.png'  # Путь к изображению логотипа

    # # Отображение логотипа в основной части приложения
    from PIL import Image
    # Загрузка логотипа
    logo = Image.open(logo_image)
    # Изменение размера логотипа
    resized_logo = logo.resize((100, 100))
    # Отображаем лого измененного небольшого размера
    st.image(resized_logo)
    # Указываем название и заголовок Streamlit приложения
    st.title('Чат с YaGPT')
    st.warning('Это Playground для общения с YandexGPT')

    # вводить все credentials в графическом интерфейсе слева
    # Sidebar contents
    with st.sidebar:
        st.title('\U0001F917\U0001F4ACYaGPT чат-бот')
        st.markdown('''
        ## О программе
        Данный YaGPT-бот использует следующие компоненты:
        - [Yandex GPT](https://cloud.yandex.ru/services/yandexgpt)
        - [Yandex GPT for Langchain](https://pypi.org/project/yandex-chain/)
        - [Streamlit](https://streamlit.io/)
        - [LangChain](https://python.langchain.com/)
        ''')
    global  yagpt_folder_id, yagpt_api_id, yagpt_api_key

    folder_id = ""
    api_id = ""
    api_key = ""

    # использовать системные переменные из облака streamlit (secrets)  
    # folder_id = st.secrets["yagpt_folder_id"]
    # api_id = st.secrets["yagpt_api_id"]
    # api_key = st.secrets["yagpt_api_key"]

    # load your credentials from .env file
    # load_dotenv()

    # yagpt_folder_id = os.getenv("YAGPT_FOLDER_ID")
    # yagpt_api_id = os.getenv("YAGPT_API_ID")
    # yagpt_api_key = os.getenv["YAGPT_API_KEY"]

    yagpt_folder_id = st.sidebar.text_input("YAGPT_FOLDER_ID", type='password', value=folder_id)
    yagpt_api_id = st.sidebar.text_input("YAGPT_API_ID", type='password', value=api_id)
    yagpt_api_key = st.sidebar.text_input("YAGPT_API_KEY", type='password', value=api_key)

    model_list = [
      "YandexGPT Lite",
      "YandexGPT"      
    ]    
    selected_model = 0
    selected_model = st.sidebar.radio("[Модель для работы:](https://cloud.yandex.ru/ru/docs/yandexgpt/concepts/models)", model_list, index=selected_model, key="index")     
    
    # yagpt_prompt = st.sidebar.text_input("Промпт-инструкция для YaGPT")
    yagpt_temperature = st.sidebar.slider("YaGPT температура", 0.0, 1.0, 0.6)
    yagpt_max_tokens = st.sidebar.slider("YaGPT макс. кол-во токенов", 200, 8000, 5000)


    # Выводим предупреждение, если пользователь не указал свои учетные данные
    if not yagpt_api_key or not yagpt_folder_id or not yagpt_api_id:
        st.warning(
            "Пожалуйста, задайте свои учетные данные (в secrets/.env или в раскрывающейся панели слева) для запуска этого приложения.")

    # Логика обработки сообщений от пользователей
    # инициализировать историю чата, если ее пока нет 
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # инициализировать состояние готовности, если его пока нет
    if 'ready' not in st.session_state:
        st.session_state['ready'] = True

    if st.session_state['ready']:

        # обращение к модели YaGPT

        if selected_model==0: 
            model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt-lite/latest"
        else:
            model_uri = "gpt://"+str(yagpt_folder_id)+"/yandexgpt/latest"

        print(model_uri)
        # llm = YandexLLM(api_key=yagpt_api_key, folder_id=yagpt_folder_id, temperature = yagpt_temperature, max_tokens=yagpt_max_tokens)        

        # промпт без учета памяти диалога
        # prompt = ChatPromptTemplate.from_template(
        #     "{topic}"
        # )

        # промпт с учетом памяти
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Ты полезный чат-бот"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        memory = ConversationBufferMemory(return_messages=True)
        memory.load_memory_variables({})

        output_parser = StrOutputParser()
        # model = YandexLLM(api_key=yagpt_api_key, folder_id = folder_id, temperature = yagpt_temperature, max_tokens=8000, use_lite = False)
        model = ChatYandexGPT(api_key=yagpt_api_key, model_uri=model_uri, temperature = yagpt_temperature)

        # llm chain без учета памяти
        # llm_chain = (
        #     {"question": RunnablePassthrough()} 
        #     | prompt
        #     | model
        #     | output_parser
        # )

        # llm chain с учетом памяти
        llm_chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
        )    

        # str2 = """Вопрос: {question}
        # Твой ответ:"
        # """
        # template = f"{yagpt_prompt} {str2}"
        # print(template)   
        # prompt = PromptTemplate(template=template, input_variables=["question"])
        # llm_chain = LLMChain(prompt=prompt, llm=llm)


        if 'generated' not in st.session_state:
            st.session_state['generated'] = [
                "Что бы вы хотели узнать?"]

        if 'past' not in st.session_state:
            st.session_state['past'] = ["Привет!"]

        # контейнер для истории чата
        response_container = st.container()

        # контейнер для текстового поля
        container = st.container()

        with container:
            with st.form(key='my_form', clear_on_submit=True):
                user_input = st.text_input(
                    "Вопрос:", placeholder="Привет! Как дела?", key='input')
                submit_button = st.form_submit_button(label='Отправить')

            if submit_button and user_input:
                # отобразить загрузочный "волчок"
                with st.spinner("Думаю..."):
                    print("История чата: ", st.session_state['chat_history'])
                    # output = llm_chain.run(
                    #     {"question": user_input})
                    inputs = {"input": user_input}
                    output = llm_chain.invoke(inputs)

                    print(type(output))

                    # print(output)
                    memory.save_context(inputs, {"output": output})
                    memory.load_memory_variables({})

                    st.session_state['past'].append(user_input)
                    st.session_state['generated'].append(output)

                    # # обновляем историю чата с помощью вопроса пользователя и ответа от бота
                    st.session_state['chat_history'].append(
                        {"вопрос": user_input, "ответ": output})

        if st.session_state['generated']:
            with response_container:
                for i in range(len(st.session_state['generated'])):
                    message(st.session_state["past"][i], is_user=True, key=str(
                        i) + '_user')
                    message(st.session_state["generated"][i], key=str(
                        i))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # st.write(f"Что-то пошло не так. Возможно, не хватает входных данных для работы. {str(e)}")
        st.write(f"Не хватает входных данных для продолжения работы. См. панель слева.")