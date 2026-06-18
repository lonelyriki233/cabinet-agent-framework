.PHONY: test demo gate

test:
	python3 -m unittest discover -s tests -v

demo:
	python3 -m agent_framework.cli init
	python3 -m agent_framework.cli intake --request "为高性能数据分析平台设计图表大数据渲染方案，需要调研技术选型、性能取舍和维护策略"
	python3 -m agent_framework.cli tasks
	python3 -m agent_framework.cli tick --mode prompt

gate:
	python3 -m agent_framework.cli gate
