import json
import openai
from tqdm import tqdm
import time

openai.api_key = "API_KEY" 

def generate_evidence_and_label(claim):
    """
    Hàm tạo bằng chứng và nhãn cho một nhận định sử dụng GPT-4
    
    Args:
        claim (str): Nhận định cần tạo bằng chứng
        
    Returns:
        tuple: (bằng chứng, nhãn) hoặc (None, None) nếu có lỗi
    """
    prompt = f"""Hãy phân tích và tạo bằng chứng cho nhận định sau đây. Bằng chứng phải có tính xác thực và liên quan trực tiếp đến nhận định.
    
    Nhận định: {claim}
    
    Yêu cầu về bằng chứng:
    1. Phải có mối quan hệ rõ ràng và trực tiếp với nhận định
    2. Độ dài từ 20-100 từ
    3. Phải dựa trên sự thật và có tính khách quan
    4. Phải được viết bằng tiếng Việt
    5. Nên bao gồm các thông tin cụ thể như số liệu, nguồn tin, hoặc sự kiện thực tế
    
    Hãy trả lời theo định dạng JSON sau:
    {{
        "evidence": "bằng chứng của bạn ở đây",
        "label": "SUPPORTS hoặc REFUTES"
    }}
    
    Lưu ý về nhãn:
    - SUPPORTS: Bằng chứng xác nhận nhận định là đúng
    - REFUTES: Bằng chứng cho thấy nhận định không chính xác
    """
    
    try:
        # Gọi API GPT-4 để tạo bằng chứng và nhãn
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý kiểm tra thông tin, chuyên tạo bằng chứng và gán nhãn cho các nhận định. Bằng chứng phải có mối quan hệ rõ ràng với nhận định, độ dài từ 20-100 từ, và dựa trên sự thật."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Lấy kết quả từ response và chuyển đổi thành dictionary
        result = response.choices[0].message.content
        result_dict = json.loads(result)
        
        # Kiểm tra độ dài của bằng chứng
        evidence = result_dict["evidence"]
        word_count = len(evidence.split())
        if word_count < 20 or word_count > 100:
            print(f"Cảnh báo: Bằng chứng có {word_count} từ, nằm ngoài khoảng 20-100 từ")
            
        return evidence, result_dict["label"]
    
    except Exception as e:
        print(f"Lỗi khi tạo bằng chứng cho nhận định: {e}")
        return None, None

def main():
    """
    Hàm chính để xử lý tất cả các nhận định
    - Đọc nhận định từ file claim_cleaned.json
    - Tạo bằng chứng và nhãn cho từng nhận định
    - Lưu kết quả vào file data_social.json
    """
    # Đọc các nhận định từ file
    with open('create_data/crawl_data/claim_cleaned.json', 'r', encoding='utf-8') as f:
        claims = json.load(f)
    
    # Khởi tạo hoặc đọc dữ liệu hiện có
    try:
        with open('create_data/crawl_data/data_social.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    # Xử lý từng nhận định
    for claim_data in tqdm(claims, desc="Đang xử lý các nhận định"):
        claim = claim_data["claim"]
        
        if any(item["claim"] == claim for item in data):
            continue
        
        evidence, label = generate_evidence_and_label(claim)
        
        if evidence and label:
            data.append({
                "claim": claim,
                "evidence": evidence,
                "label": label
            })
            
            with open('create_data/crawl_data/data_social.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            time.sleep(1)

if __name__ == "__main__":
    main()
