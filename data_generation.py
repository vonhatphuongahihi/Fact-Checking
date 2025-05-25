import json
import time
import os
from typing import Dict
from tqdm import tqdm
import openai

openai.api_key = ""

def generate_claim_evidence_pair() -> Dict:
    prompt = """
    Tạo một cặp claim-evidence cho bài toán fact-checking với các yêu cầu sau:
    1. Claim phải là một tuyên bố có thể kiểm chứng được, độ dài từ 10-80 từ
    2. Evidence phải là thông tin thực tế có thể dùng để xác minh claim, độ dài từ 20-100 từ
    3. Label phải là một trong hai giá trị: SUPPORTS hoặc REFUTES
    
    Các yêu cầu bổ sung:
    - Claim phải đa dạng về chủ đề: khoa học, lịch sử, địa lý, văn hóa, kinh tế, chính trị, y tế, giáo dục, thể thao, công nghệ
    - Evidence phải chứa thông tin cụ thể, số liệu, nguồn tham khảo khi có thể
    - Không tạo các claim quá hiển nhiên hoặc quá phức tạp
    - Đảm bảo tính logic giữa claim và evidence
    - Tránh các claim có tính chất chủ quan hoặc không thể kiểm chứng
    
    Dữ liệu theo hướng sự kiện thực tế phải thỏa mãn:
    - Gắn với thời gian, bối cảnh lịch sử cụ thể
    - Là tuyên bố đã hoặc có thể xảy ra, không phải tri thức khái quát
    - Có thể kiểm chứng được bằng nguồn thông tin cụ thể (sách, báo, tài liệu, wikipedia)
    - Thường liên quan đến diễn biến, nhân vật, tổ chức, mốc thời gian
    - Phải mang tính thời sự
    
    Trả về kết quả theo định dạng JSON:
    {
        "claim": "tuyên bố cần kiểm chứng",
        "evidence": "bằng chứng để kiểm chứng",
        "label": "SUPPORTS/REFUTES"
    }
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4",  
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia fact-checking với kiến thức sâu rộng về nhiều lĩnh vực. Bạn có khả năng tạo ra các claim và evidence đa dạng, chính xác và có thể kiểm chứng được."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Tăng temperature để tạo mẫu đa dạng hơn
            max_tokens=500    # Tăng max_tokens để có đủ không gian cho evidence dài
        )
        content = response.choices[0].message.content.strip()
        try:
            result = json.loads(content)
            if len(result["claim"].split()) < 10 or len(result["claim"].split()) > 80:
                print(f"Claim không đúng độ dài: {len(result['claim'].split())} từ")
                return None
            if len(result["evidence"].split()) < 20 or len(result["evidence"].split()) > 100:
                print(f"Evidence không đúng độ dài: {len(result['evidence'].split())} từ")
                return None
            if result["label"] not in ["SUPPORTS", "REFUTES"]:
                print(f"Label không hợp lệ: {result['label']}")
                return None
            return result
        except json.JSONDecodeError:
            print(f"Không parse được JSON:\n{content}")
            return None
    except Exception as e:
        print(f"Lỗi khi tạo mẫu: {e}")
        return None

def generate_dataset(num_samples: int = 100, output_file: str = "data/generated_dataset.json", batch_size: int = 10):
    dataset = []
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"Bắt đầu tạo {num_samples} mẫu dữ liệu...")

    for batch_start in tqdm(range(0, num_samples, batch_size)):
        batch_end = min(batch_start + batch_size, num_samples)
        batch_data = []
        for _ in range(batch_start, batch_end):
            sample = generate_claim_evidence_pair()
            if sample:
                batch_data.append(sample)
            time.sleep(1) 
        dataset.extend(batch_data)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        print(f"Đã tạo xong {len(dataset)}/{num_samples} mẫu dữ liệu")

    print(f"Hoàn thành! Đã tạo {len(dataset)} mẫu dữ liệu và lưu vào {output_file}")

if __name__ == "__main__":
    generate_dataset(num_samples=100, batch_size=10)