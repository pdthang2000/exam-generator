AI Exam Generator — System Architecture + Tech Stack (ChromaDB RAG Edition)
1) Tổng quan
AI Exam Generator là một mini-product tạo đề thi bằng AI theo hướng có kiểm soát chất lượng, có khả năng truy xuất ngữ cảnh từ tài liệu bằng RAG, và có thể mở rộng dần thành hệ thống question bank cho giáo dục hoặc training nội bộ.

Khác với một app chỉ “generate câu hỏi”, hệ thống này được thiết kế như một pipeline hoàn chỉnh gồm:

ingest tài liệu,
chunking và embedding,
lưu vector vào ChromaDB,
retrieve ngữ cảnh liên quan,
generate câu hỏi,
verify đáp án,
review chất lượng,
xuất output theo schema chuẩn.
Chroma rất phù hợp cho kiến trúc này vì hỗ trợ lưu embeddings kèm metadata, tìm kiếm dense/sparse/hybrid, metadata filtering, và có thể chạy local, self-host hoặc cloud tùy giai đoạn phát triển. Chroma Docs

2) Mục tiêu hệ thống
Hệ thống hướng đến các mục tiêu chính sau:

Grounded generation: câu hỏi được sinh dựa trên các chunk tài liệu đã retrieve, thay vì sinh “trôi nổi”.
Quality control: mỗi câu hỏi đều được kiểm tra mức độ bám context, độ rõ nghĩa, và độ hợp lý.
Structured output: đầu ra có schema rõ ràng để dễ hiển thị UI, export JSON/CSV/PDF và tích hợp về sau.
Scalability for hackathon MVP: MVP chạy local được, nhưng kiến trúc đủ đẹp để thuyết trình như một mini-product có thể mở rộng.
3) Use case chính
Use case MVP
Người dùng: - paste một đoạn tài liệu hoặc upload tài liệu, - chọn loại đề: MCQ / True-False / Short Answer, - chọn số lượng câu hỏi, - chọn độ khó, - hệ thống sinh đề, - hệ thống kiểm tra chất lượng nội bộ, - trả về đề hoàn chỉnh kèm đáp án, explanation và nhãn chất lượng.

Use case mở rộng
ingest nhiều tài liệu cùng lúc,
tạo đề từ từng chapter hoặc từng section,
tái sử dụng tài liệu thành một knowledge base,
tạo nhiều đề khác nhau từ cùng một nguồn học liệu,
mở rộng sang teacher dashboard hoặc question bank.
4) Kiến trúc hệ thống tổng thể
4.1. Logical architecture
User Interface
    ↓
Input & Settings Layer
    ↓
Document Ingestion Layer
    ↓
Chunking + Metadata Enrichment
    ↓
Embedding Layer
    ↓
ChromaDB Vector Store
    ↓
Retriever Layer
    ↓
Question Generation Layer
    ↓
Distractor / Answer Construction Layer
    ↓
Verification & Quality Review Layer
    ↓
Formatting / Structured Output Layer
    ↓
Export / Presentation Layer
Giải thích từng tầng
1. User Interface
Giao diện cho phép người dùng: - nhập hoặc upload tài liệu, - chọn loại đề, - chọn số câu, - chọn difficulty, - xem đề đã sinh, - export kết quả.

2. Input & Settings Layer
Tầng này nhận và chuẩn hóa input từ người dùng, ví dụ: - raw text, - uploaded document, - exam type, - number of questions, - difficulty, - language.

3. Document Ingestion Layer
Tầng này chịu trách nhiệm: - đọc nội dung file, - convert sang text, - làm sạch dữ liệu, - chia tài liệu thành các đơn vị có thể xử lý.

4. Chunking + Metadata Enrichment
Text được chia chunk để phục vụ retrieval. Mỗi chunk được gắn metadata như: - document_id - source_name - subject - section - difficulty_hint - chunk_index - language

5. Embedding Layer
Mỗi chunk được encode thành vector embedding để đưa vào vector store.

6. ChromaDB Vector Store
Chroma giữ: - embeddings, - document text, - metadata, - collection theo từng project hoặc theo từng user/session.

Chroma hỗ trợ lưu document + metadata, query similarity, metadata filtering, và có thể chạy local hoặc self-host/cloud. Chroma Docs

7. Retriever Layer
Khi user yêu cầu tạo đề, hệ thống: - tạo truy vấn retrieval, - lấy ra top-k chunks liên quan, - filter theo metadata nếu cần, - cung cấp ngữ cảnh đã retrieve cho bước generate.

LangChain tích hợp trực tiếp với Chroma, hỗ trợ persist_directory cho local persistence và as_retriever() để đưa vector store vào pipeline retrieval một cách gọn gàng. LangChain

8. Question Generation Layer
Dựa trên retrieved chunks, hệ thống sinh: - câu hỏi, - đáp án nền, - candidate items.

9. Distractor / Answer Construction Layer
Nếu là MCQ, hệ thống sinh distractors và tạo options A/B/C/D. Nếu là Short Answer hoặc True/False, hệ thống sẽ sinh theo pipeline riêng.

10. Verification & Quality Review Layer
Đây là tầng tạo khác biệt cho sản phẩm. Hệ thống kiểm tra: - câu hỏi có answerable từ context hay không, - đáp án có bám đúng đoạn retrieve hay không, - distractors có hợp lý không, - câu có rõ nghĩa và đúng format không.

11. Formatting / Structured Output Layer
Sau khi câu hỏi đã đạt điều kiện, hệ thống format output thành JSON schema cố định để: - hiển thị UI, - export, - dùng cho API, - dễ validate.

Structured Outputs của OpenAI rất phù hợp để bắt model trả JSON đúng schema, tránh thiếu key hoặc sinh enum sai. OpenAI

12. Export / Presentation Layer
Hiển thị và xuất ra: - JSON, - CSV, - PDF hoặc DOCX về sau, - màn hình demo đẹp để trình bày hackathon.

4.2. Deployment architecture cho hackathon MVP
Recommended MVP deployment
[Streamlit UI]
     │
     ▼
[Python App / Orchestration Layer]
     ├── Ingestion & Chunking
     ├── Embedding Service
     ├── LangChain Retriever
     ├── HF Models (QG / QA / Distractors)
     ├── OpenAI API (rewrite / explanation / JSON formatting)
     └── Export Layer
             │
             ▼
       [ChromaDB Persistent Local Store]
Vì sao nên chọn kiểu này
dễ build trong 4–5 tuần,
ít DevOps overhead,
vẫn đủ đẹp để thuyết trình kiến trúc,
có thể chạy local trong demo,
dễ nâng cấp lên FastAPI + React sau này.
5) Tech stack đề xuất
5.1. Recommended stack cho hackathon
Thành phần	Đề xuất	Vai trò
Frontend / UI	Streamlit	Giao diện nhập liệu, hiển thị đề, demo nhanh
Core language	Python	Toàn bộ pipeline chính
Orchestration	LangChain	Retriever, chaining, tích hợp Chroma
Workflow graph	LangGraph (optional)	Trực quan hóa flow nhiều bước
Vector Database	ChromaDB	Lưu embeddings, metadata, retrieval
Embeddings	text-embedding-3-small hoặc sentence-transformers/all-MiniLM-L6-v2	Tạo vector cho chunk tài liệu
Question Generation	iarfmoose/t5-base-question-generator	Sinh câu hỏi từ context + answer
QA Verification	deepset/roberta-base-squad2	Kiểm tra answerability / extractive QA
Distractor Generation	fares7elsadek/t5-base-distractor-generation	Sinh 3 phương án nhiễu cho MCQ
Rewrite / Explanation / Formatting	OpenAI API	Làm mượt, thêm explanation, format JSON
Validation	Pydantic	Khóa schema output
Export	pandas	Export CSV/JSON
File parsing	PyMuPDF / python-docx / unstructured (optional)	Đọc PDF/DOCX
5.2. Recommended production-style upgrade path
Thành phần	MVP	Giai đoạn nâng cấp
UI	Streamlit	React
Backend	Python app	FastAPI
Vector DB	Chroma local persistent	Chroma server / cloud
Metadata DB	Optional local JSON/SQLite	PostgreSQL
File storage	Local / folder-based	Object storage
Workflow	LangChain	LangGraph + async workers
Export	JSON / CSV	PDF / DOCX
Auth	None	Clerk / Firebase / Auth0
6) Mô hình / model đầy đủ cho từng thành phần
6.1. Embedding models
Option A — OpenAI text-embedding-3-small
text-embedding-3-small là model embedding cải tiến của OpenAI, phù hợp cho search, clustering, recommendation, anomaly detection và classification. Đây là lựa chọn rất hợp cho RAG khi bạn cần chất lượng ổn định và API dễ dùng. OpenAI Models

Khi nên dùng: - cần chất lượng embedding ổn định, - muốn giảm rủi ro triển khai local model, - cần time-to-market nhanh cho hackathon.

Option B — sentence-transformers/all-MiniLM-L6-v2
Model này map câu và đoạn văn thành không gian vector dense 384 chiều, phù hợp cho semantic search, information retrieval, clustering và sentence similarity. Hugging Face

Khi nên dùng: - muốn chạy local, - cần tiết kiệm chi phí API, - tài nguyên phần cứng vừa phải.

Khuyến nghị: - Hackathon cần ổn định: ưu tiên OpenAI embeddings. - Hackathon cần rẻ hoặc offline hơn: ưu tiên MiniLM.

6.2. Question Generation model
iarfmoose/t5-base-question-generator
Đây là model sequence-to-sequence dựa trên t5-base, nhận answer + context làm input và sinh question làm output. Model được fine-tune cho dạng reading-comprehension question generation và hoạt động tốt nhất khi answer là câu hoặc phrase đầy đủ. Hugging Face

Input format:

<answer> answer text here <context> context text here
Vai trò trong hệ thống: - sinh câu hỏi ban đầu từ retrieved chunk, - dùng cho MCQ và Short Answer, - có thể generate nhiều candidates rồi filter.

6.3. Distractor Generation model
fares7elsadek/t5-base-distractor-generation
Model này là một bản T5-base fine-tune cho nhiệm vụ sinh distractors. Nó nhận question + context + correct answer và sinh ra 3 distractors plausible trong một lần chạy, rất phù hợp để tạo MCQ. Hugging Face

Input pattern:

question <sep> context <sep> correct_answer
Vai trò trong hệ thống: - sinh phương án nhiễu cho MCQ, - giúp output bớt phụ thuộc hoàn toàn vào LLM rewrite, - có thể kết hợp rule-based filtering sau khi sinh.

6.4. QA Verification model
deepset/roberta-base-squad2
Model này là roberta-base fine-tune trên SQuAD 2.0 cho extractive question answering, bao gồm cả các trường hợp unanswerable questions. Vì vậy nó rất phù hợp để kiểm tra một câu hỏi có thực sự được trả lời từ context hay không. Hugging Face

Vai trò trong hệ thống: - kiểm tra answerability, - verify đáp án so với retrieved context, - hỗ trợ quality label kiểu “Grounded / Needs Review / Bad”.

6.5. LLM layer
OpenAI API — đề xuất dùng cho
rewrite câu hỏi cho tự nhiên hơn,
thêm explanation,
chuẩn hóa ngôn ngữ,
format JSON output,
review nhẹ chất lượng câu hỏi.
Structured Outputs
Structured Outputs giúp model tuân thủ đúng JSON Schema do bạn định nghĩa, tránh thiếu key hoặc trả format lỗi. Điều này rất có giá trị với AI Exam Generator vì output cần ổn định theo các field như question, options, answer, difficulty, quality_label, explanation. OpenAI

Vai trò của LLM trong hệ thống: - không thay toàn bộ pipeline truyền thống, - mà làm lớp polish, explanation, structured formatting và review mềm.

6.6. Optional models / modules mở rộng
Zero-shot classification
Có thể thêm zero-shot classifier để gán nhãn: - subject, - difficulty, - exam type suggestion.

Grammar / style review
Có thể dùng LLM hoặc rule-based + language tool để phát hiện: - câu mơ hồ, - ngữ pháp chưa tốt, - lựa chọn nhiễu bất hợp lý.

NLI-based consistency check
Nếu muốn nâng chất lượng, có thể thêm NLI step để kiểm tra: - answer có được support bởi context không, - explanation có mâu thuẫn với source chunk không.

7) Thiết kế collections và dữ liệu trong ChromaDB
7.1. Collection strategy
Option A — One collection per project
Ví dụ: - exam_generator_project_biology - exam_generator_project_history

Ưu điểm: - dễ quản lý theo demo/project, - phù hợp hackathon.

Option B — One collection per user/session
Ví dụ: - user_001_exam_docs - session_2026_07_demo

Ưu điểm: - dễ mở rộng multi-user sau này.

Khuyến nghị cho MVP: - dùng one collection per project hoặc per demo session.

7.2. Metadata schema đề xuất
{
  "document_id": "bio_chapter_01",
  "source_name": "Cell Biology Notes",
  "subject": "Biology",
  "section": "Mitochondria",
  "difficulty_hint": "Medium",
  "chunk_index": 3,
  "language": "en"
}
Ý nghĩa các field
document_id: ID tài liệu gốc
source_name: tên file hoặc tên nguồn
subject: môn học / domain
section: phần nội dung nhỏ hơn
difficulty_hint: gợi ý độ khó
chunk_index: thứ tự chunk
language: ngôn ngữ tài liệu
7.3. Dữ liệu lưu trong mỗi record
Mỗi record trong Chroma nên gồm: - id - document - embedding - metadata

Ví dụ conceptually:

{
  "id": "bio_ch1_chunk_003",
  "document": "Mitochondria are membrane-bound organelles responsible for ATP production...",
  "metadata": {
    "document_id": "bio_chapter_01",
    "source_name": "Cell Biology Notes",
    "subject": "Biology",
    "section": "Mitochondria",
    "difficulty_hint": "Medium",
    "chunk_index": 3,
    "language": "en"
  }
}
8) Flow dự án / project flow hoàn chỉnh
8.1. End-to-end product flow
User nhập hoặc upload tài liệu
        ↓
Tiền xử lý văn bản
        ↓
Chunking + metadata enrichment
        ↓
Embedding
        ↓
Lưu chunk vào ChromaDB
        ↓
User chọn loại đề / số lượng câu / độ khó
        ↓
Retriever lấy top-k chunk liên quan
        ↓
Question generation tạo candidate questions
        ↓
Distractor generation tạo phương án nhiễu (nếu MCQ)
        ↓
QA verification kiểm tra answerability / grounding
        ↓
LLM rewrite + explanation + structured formatting
        ↓
Quality labeling
        ↓
Hiển thị đề hoàn chỉnh + export
8.2. Detailed pipeline theo từng bước
Step 1 — Ingest input
Nguồn input có thể là: - pasted text, - PDF, - DOCX, - TXT.

Step 2 — Clean & normalize
bỏ ký tự rác,
chuẩn hóa whitespace,
tách section nếu có heading,
phát hiện language nếu cần.
Step 3 — Chunking
Khuyến nghị chunk theo: - 300–800 tokens, - overlap 50–100 tokens, - ưu tiên giữ nguyên câu hoàn chỉnh.

Step 4 — Generate embeddings
dùng text-embedding-3-small hoặc all-MiniLM-L6-v2,
tạo vector cho từng chunk.
Step 5 — Index into Chroma
add documents,
add metadata,
persist local collection.
Step 6 — Retrieval
Tùy lựa chọn user, build truy vấn retrieval như: - “retrieve context for biology MCQ medium difficulty” - hoặc retrieve theo section cụ thể.

Top-k đề xuất cho MVP: - k = 3 đến k = 6.

Step 7 — Build answer candidates
Có 2 hướng: - extract answer spans từ chunk, - hoặc dùng QA extraction để xác định answer candidate trước khi generate question.

Step 8 — Generate question
Dùng iarfmoose/t5-base-question-generator với cặp: - answer, - context chunk.

Step 9 — Generate distractors
Dùng fares7elsadek/t5-base-distractor-generation cho MCQ. Sau đó post-process để: - loại distractor trùng đáp án, - loại distractor quá giống nhau, - đảm bảo đủ 4 lựa chọn.

Step 10 — Verify answerability
Dùng deepset/roberta-base-squad2 để kiểm tra: - nếu hỏi lại bằng question này trên context, answer có xuất hiện hợp lý không, - confidence có đủ không, - câu có phải unanswerable không.

Step 11 — LLM refinement
Dùng OpenAI để: - viết lại câu hỏi tự nhiên hơn, - thêm explanation, - format JSON, - chuẩn hóa wording.

Step 12 — Quality label
Gán nhãn ví dụ: - Good - Needs Review - Bad

Theo các tín hiệu: - QA confidence, - distractor diversity, - grammar/clarity, - schema validity.

Step 13 — Render & export
Hiển thị trên UI và export ra: - JSON, - CSV, - PDF/DOCX về sau.

9) Flow riêng cho từng loại đề
9.1. MCQ flow
Retrieve context
    ↓
Select answer candidate
    ↓
Generate question
    ↓
Generate 3 distractors
    ↓
Assemble 4 options
    ↓
Verify answerability
    ↓
Rewrite + explanation
    ↓
Return MCQ item
9.2. True/False flow
Retrieve context
    ↓
Extract factual statement
    ↓
Create true version or mutate into false version
    ↓
Verify statement against context
    ↓
Return True/False item
9.3. Short Answer flow
Retrieve context
    ↓
Select answer span / key concept
    ↓
Generate short-answer question
    ↓
Verify with extractive QA
    ↓
Rewrite + explanation
    ↓
Return short-answer item
10) Output schema đề xuất
{
  "exam_id": "exam_001",
  "subject": "Biology",
  "difficulty": "Medium",
  "type": "MCQ",
  "source": {
    "document_id": "bio_chapter_01",
    "section": "Mitochondria",
    "chunk_id": "bio_ch1_chunk_003"
  },
  "question": "What is the primary function of mitochondria in the cell?",
  "options": [
    "Protein synthesis",
    "Energy production",
    "Waste removal",
    "DNA packaging"
  ],
  "answer": "Energy production",
  "explanation": "Mitochondria produce ATP, which is the cell's main form of usable energy.",
  "quality_label": "Good",
  "quality_signals": {
    "qa_confidence": 0.89,
    "context_alignment": true,
    "distractor_quality": "acceptable"
  }
}
11) Cấu trúc module / folder gợi ý
ai-exam-generator/
│
├── app/
│   ├── ui/
│   │   └── streamlit_app.py
│   ├── orchestration/
│   │   ├── pipeline.py
│   │   ├── retrieval.py
│   │   ├── generation.py
│   │   ├── verification.py
│   │   └── formatting.py
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   ├── vectorstore/
│   │   ├── chroma_client.py
│   │   └── indexing.py
│   ├── models/
│   │   ├── embeddings.py
│   │   ├── qg_model.py
│   │   ├── distractor_model.py
│   │   ├── qa_model.py
│   │   └── llm_client.py
│   ├── schemas/
│   │   └── exam_item.py
│   ├── export/
│   │   ├── json_export.py
│   │   ├── csv_export.py
│   │   └── pdf_export.py
│   └── utils/
│       └── logging.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── chroma/
│
├── notebooks/
├── tests/
├── requirements.txt
└── README.md
12) Quy tắc chọn model trong hệ thống
Khi nào dùng embedding local
Dùng all-MiniLM-L6-v2 nếu: - muốn tiết kiệm chi phí, - demo local, - không muốn phụ thuộc API cho embeddings.

Khi nào dùng embedding API
Dùng text-embedding-3-small nếu: - muốn retrieval ổn định hơn, - cần giảm thời gian tuning embedding local, - ưu tiên chất lượng hơn chi phí.

Khi nào dùng LLM nhiều hơn
Dùng OpenAI nhiều hơn nếu: - muốn wording đẹp, - muốn explanation rõ, - muốn structured JSON output đáng tin cậy.

Khi nào giữ pipeline model chuyên dụng
Giữ Hugging Face models nếu: - muốn giải thích pipeline rõ ràng với judge, - muốn chứng minh đây là hệ thống AI engineering, không chỉ một prompt, - muốn có tầng verification rõ ràng.

13) Chỉ số đánh giá nên có
Để hệ thống thuyết phục hơn khi thuyết trình, nên đo:

Question usability rate: bao nhiêu câu sau filter được giữ lại
Grounding rate: bao nhiêu câu có thể verify lại từ context
Average generation time
MCQ completion rate: bao nhiêu câu có đủ options hợp lệ
Manual quality score: đánh giá thủ công bởi team hoặc tester
14) Rủi ro kỹ thuật và cách giảm thiểu
Rủi ro 1 — Chunk retrieve chưa đúng
Giảm thiểu: - tune chunk size, - thêm overlap, - filter metadata, - tăng top-k vừa phải.

Rủi ro 2 — Distractors quá yếu
Giảm thiểu: - hậu xử lý loại distractor trùng, - fallback LLM rewrite, - thêm semantic diversity check.

Rủi ro 3 — Output JSON lỗi format
Giảm thiểu: - Pydantic validation, - Structured Outputs từ OpenAI, - retry nhẹ nếu schema fail. OpenAI

Rủi ro 4 — Demo chậm
Giảm thiểu: - pre-index sample documents, - cache embeddings, - cache retriever, - chuẩn bị sample inputs tốt.

15) Lộ trình phát triển sau MVP
Phase 1 — Hackathon MVP
Streamlit
Chroma local persistent
basic RAG
MCQ + TF + Short Answer
JSON/CSV export
Phase 2 — Mini-product v2
FastAPI + React
upload nhiều file
teacher review mode
analytics dashboard
PDF export
Phase 3 — Productization
multi-user auth
persistent user projects
question bank
recommendation engine
LMS integration
16) Kết luận
Kiến trúc phù hợp nhất cho AI Exam Generator dùng ChromaDB là kiến trúc RAG + generation + verification + structured output.

Điểm mạnh của hướng này là: - có retrieval-based grounding, - có vector memory bằng Chroma, - có quality control chứ không chỉ generation, - đủ gọn để làm MVP trong 5 tuần, - đủ đẹp để pitch như một mini-product có tính mở rộng.

Về stack, cấu hình khuyến nghị cho hackathon là: - Streamlit cho UI, - Python + LangChain cho orchestration, - ChromaDB cho vector store, - OpenAI embeddings hoặc MiniLM cho embeddings, - iarfmoose/t5-base-question-generator cho question generation, - fares7elsadek/t5-base-distractor-generation cho distractors, - deepset/roberta-base-squad2 cho QA verification, - OpenAI API cho rewrite, explanation và structured JSON output. Chroma Docs LangChain Hugging Face Hugging Face Hugging Face OpenAI Models OpenAI

Nếu cần mở rộng tiếp, hệ thống này có thể tiến hóa rất tự nhiên thành: - question bank, - assessment engine, - teacher assistant, - hoặc plugin cho nền tảng edtech/LMS.