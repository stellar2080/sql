import streamlit as st

st.title("知识库")

@st.dialog("上传文件到知识库",width="large")
def upload():
    uploaded_files = st.file_uploader(
        "文件类型限制为txt文件，支持同时上传多个文件", accept_multiple_files=True
    )
    is_upload = st.button(label="上传",use_container_width=True)
    if is_upload:
        manager = st.session_state.manager
        with st.container(height=300):
            for uploaded_file in uploaded_files:
                st.write(f'解析文件{uploaded_file.name}...')
                file_content = uploaded_file.read().decode("utf-8")
                lines = file_content.splitlines()
                for line in lines:
                    line = line.rstrip()
                    st.write(line)
                    manager.add_doc_to_vectordb(line)
                st.write(f'解析文件{uploaded_file.name}完毕.')

if st.button("上传文件到知识库"):
    upload()

        