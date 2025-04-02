<script lang="ts" setup>
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { ElContainer } from 'element-plus'

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts

const accData = [
  33.88, 39.57, 42.71, 45.24, 46.93, 48.57, 49.94, 51.14, 52.14, 53.32, 54.08, 54.9, 55.55, 56.48,
  57.16, 57.88, 58.19, 58.74, 59.29, 59.59, 60.09, 60.71, 60.62, 61.09, 61.44, 61.52, 62.26, 62.56,
  62.46, 62.95, 63.12, 63.49, 63.48, 64.03, 63.97, 64.32, 64.56, 64.66, 64.46, 64.97, 65.25, 65.32,
  65.17, 65.34, 65.44, 65.81, 65.95, 66.36, 66.16, 66.44,
].map((v) => (v + 30) / 100) // 转换为小数
const lossData = [
  0.1898, 0.1714, 0.1608, 0.1545, 0.1497, 0.146, 0.1423, 0.1392, 0.136, 0.1338, 0.1312, 0.1293,
  0.127, 0.1251, 0.1231, 0.1217, 0.1197, 0.1187, 0.1169, 0.1157, 0.1147, 0.1132, 0.1124, 0.1111,
  0.1108, 0.1097, 0.1086, 0.1077, 0.1072, 0.1068, 0.1059, 0.1054, 0.1049, 0.104, 0.1036, 0.1029,
  0.1026, 0.1019, 0.1021, 0.1009, 0.1004, 0.1002, 0.1002, 0.0994, 0.0992, 0.0982, 0.0982, 0.0976,
  0.0975, 0.0968,
]
const epochs = Array.from({ length: lossData.length }, (_, i) => `第${i + 1}轮`)

const initChart = () => {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value)

  const option = {
    tooltip: { trigger: 'axis' },
    dataZoom: [
      {
        type: 'slider',
        show: false,
        realtime: true,
        startValue: 0,
        endValue: 6,
      },
    ],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      top: '10%',
      containLabel: true,
    },
    legend: [
      {
        right: '4%',
        top: 20,
        itemWidth: 10,
        itemHeight: 10,
        data: '准确度',
        textStyle: { color: '#666' },
      },
      {
        left: '4%',
        top: 20,
        itemWidth: 10,
        itemHeight: 10,
        data: '损失',
        textStyle: { color: '#666' },
      }
    ],
    xAxis: {
      type: 'category',
      data: epochs,
      axisLabel: { color: '#999' },
      axisLine: { lineStyle: { color: '#eee' } },
      axisTick: { show: false },
      splitLine: { show: false },
      boundaryGap: false,
    },
    yAxis: [
      {
        type: 'value',
        axisLabel: { color: '#999' },
        axisLine: { lineStyle: { color: '#eee' } },
        axisTick: { show: false },
        splitLine: { show: false },
        scale: true,
      },
      {
        type: 'value',
        axisLabel: { color: '#999' },
        axisLine: { lineStyle: { color: '#eee' } },
        axisTick: { show: false },
        splitLine: { show: false },
        scale: true,
      }
    ],
    series: [
      {
        name: '准确度',
        type: 'line',
        smooth: true,
        symbol: 'none',
        itemStyle: {
          color: 'rgb(129, 199, 132)',
          borderColor: '#fff',
          borderWidth: 2,
        },
        lineStyle: {
          color: 'rgb(129, 199, 132)',
          shadowColor: 'rgba(129, 199, 132, 0.3)',
          shadowBlur: 8,
          shadowOffsetY: 10,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(129, 199, 132, 0.6)' },
            { offset: 1, color: 'rgba(129, 199, 132, 0)' },
          ]),
        },
        data: accData,
      },
      {
        name: '损失',
        type: 'line',
        smooth: true,
        symbol: 'none',
        itemStyle: {
          color: 'rgb(255, 183, 77)',
          borderColor: '#fff',
          borderWidth: 2,
        },
        lineStyle: {
          color: 'rgb(255, 183, 77)',
          shadowColor: 'rgba(255, 183, 77, 0.3)',
          shadowBlur: 8,
          shadowOffsetY: 10,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 183, 77, 0.6)' },
            { offset: 1, color: 'rgba(255, 183, 77, 0)' },
          ]),
        },
        yAxisIndex: 1,
        data: lossData,
      },
    ],
  }

  chart.setOption(option)

  // 自动滚动
  const start = 0
  const visibleCount = 30
  chart.dispatchAction({
    type: 'dataZoom',
    startValue: start,
    endValue: start + visibleCount - 1,
  })
}

const subProgressColor = ref('#e6a23c')

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) chart.dispose()
})
</script>

<template>
  <el-container class="page-container">
    <el-text class="chart-title">正在进行第48轮训练</el-text>
    <el-progress
      :text-inside="true"
      :percentage="80"
      :stroke-width="24"
      :format="formatMainProgress"
      class="train-progress"
    />
    <el-progress :text-inside="true" :percentage="65" :stroke-width="24" :color="subProgressColor" class="train-progress" />

    <el-alert type="info" show-icon class="train-alert">
      <p>模型正在后台训练中，您可以：</p>
      <p>1. 最小化本窗口进行其他操作</p>
      <p>2. 随时返回查看实时进度</p>
    </el-alert>

    <el-container ref="chartContainerEl">
      <div class="chart-container">
        <div ref="chartEl" style="height: 300px"></div>
      </div>
    </el-container>
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.train-progress {
  padding-top: 12px;
  width: 50vw;
}

.train-alert {
  margin-top: 40px;
  width: 40vw;
}

.chart-title {
  padding-top: 48px;
  font-size: 24px;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.chart-container {
  width: 700px;
  margin: auto;
  align-items: flex-end;
}
</style>
