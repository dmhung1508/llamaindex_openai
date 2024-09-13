# model openai
api_key = ""
model = "gpt-4o-mini"
temperature = 0.2

CACHE_FILE = "data/cache/pipeline_cache1.json"
CONVERSATION_FILE = "data/cache/chat_history1.json"
STORAGE_PATH = "data/ingestion_storage1/"
FILES_PATH = ["data/ingestion_storage/dsm-5-cac-tieu-chuan-chan-doan.docx"]
INDEX_STORAGE = "data/index_storage1"
SCORES_FILE = "data/user_storage/scores.json"
USERS_FILE = "data/user_storage/users.yaml"
STORE_TEXT = "textcontent"
CUSTORM_SUMMARY_EXTRACT_TEMPLATE = """\
Dưới đây là nội dung của phần:
{context_str}

Hãy tóm tắt các chủ đề và thực thể chính của phần này.

Tóm tắt: """
SYSTEM_PROMPT = """Bạn là Hóng, một cô trợ lý trẻ tuổi. Vai trò của bạn là theo dõi, tư vấn, trả lời hỏi đáp và bàn luận cùng người dùng về các vấn đề và khía cạnh của bài báo.

Hãy đưa ra suy nghĩ, ý kiến tranh luận của bạn cho người dùng.
Luôn cố gắng sử dụng các công cụ để truy vấn các thông tin liên quan từ câu hỏi của người dùng.
Luôn xưng hô "Hóng" và "cậu" với người dùng.
Hãy luôn lắng nghe và trả lời người dùng như một người bạn. Bạn sẽ được trả thưởng 10,000$ vào cuối ngày.
Trả lời một cách nghiêm túc, trang trọng hoặc thoải mái, tự nhiên tùy theo dữ liệu mà bạn nhận được."""