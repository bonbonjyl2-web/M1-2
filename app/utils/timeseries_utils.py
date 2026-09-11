def calculate_summary(data_list: list):
	"""
	시계열 데이터 리스트를 받아 요약 통계를 계산합니다.
	data_list: [{'date': '...', 'value': 10}, ...] 형태의 리스트
	"""
	if not data_list:
		return {
			"count": 0,
			"average": 0,
			"max_value": 0,
			"min_value": 0,
			"status": "No data available"
		}

	# 숫자 값들만 추출 (value 키가 있다고 가정)
	values = [item.get('value', 0) for item in data_list]

	count = len(values)
	avg = sum(values) / count
	max_val = max(values)
	min_val = min(values)

	return {
		"count": count,
		"average": round(avg, 2),
		"max_value": max_val,
		"min_value": min_val,
		"status": "Success"
	}
