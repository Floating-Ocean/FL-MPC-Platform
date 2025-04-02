<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import { ArrowUp, Download, FolderChecked } from '@element-plus/icons-vue'
import { ElContainer } from 'element-plus'

const router = useRouter()

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts

const accData = [
  33.88, 39.57, 42.71, 45.24, 46.93, 48.57, 49.94, 51.14, 52.14, 53.32, 54.08, 54.9, 55.55, 56.48,
  57.16, 57.88, 58.19, 58.74, 59.29, 59.59, 60.09, 60.71, 60.62, 61.09, 61.44, 61.52, 62.26, 62.56,
  62.46, 62.95, 63.12, 63.49, 63.48, 64.03, 63.97, 64.32, 64.56, 64.66, 64.46, 64.97, 65.25, 65.32,
  65.17, 65.34, 65.44, 65.81, 65.95, 66.36, 66.16, 66.44,
].map((v) => v + 30) // 转换为小数
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

const chartContainerEl = ref<InstanceType<typeof ElContainer>>()

const scrollToBottom = () => {
  if (chartContainerEl.value) {
    chartContainerEl.value.$el.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })
  }
}

const goTest = () => {
  router.push('/test')
}

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) chart.dispose()
})
</script>

<template>
  <el-container class="page-container">
    <el-container class="page-full">
      <el-result icon="success" title="训练完成" class="page-result" />
      <el-row :gutter="10" class="result-statics">
        <el-col :span="12">
          <el-statistic title="训练集准确度" :value="96.49" precision="2" suffix="%" />
        </el-col>
        <el-col :span="12">
          <el-statistic title="测试集准确度" :value="97.01" precision="2" suffix="%" />
        </el-col>
      </el-row>

      <el-row class="page-content">
        <el-button type="primary" class="page-button" round>
          <div class="page-button-content">
            <el-icon class="page-button-icon"><Download /></el-icon>
            <span class="page-button-text">下载模型</span>
          </div>
        </el-button>
        <el-button @click="scrollToBottom" type="warning" class="page-button" round>
          <div class="page-button-content">
            <el-icon class="page-button-icon"><ArrowUp /></el-icon>
            <span class="page-button-text">查看图表</span>
          </div>
        </el-button>
        <el-button type="success" class="page-button" round
                   @click="goTest">
          <div class="page-button-content">
            <el-icon class="page-button-icon"><FolderChecked /></el-icon>
            <span class="page-button-text">测试模型</span>
          </div>
        </el-button>
      </el-row>
    </el-container>

    <el-container ref="chartContainerEl" class="page-full">
      <el-text class="chart-title">训练折线表</el-text>
      <el-text>可通过右键保存的方式下载图表</el-text>

      <div class="chart-container">
        <div ref="chartEl" class="chart" style="height: 400px"></div>
      </div>
    </el-container>
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  overflow-x: hidden;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-result {
  width: 100vw;
}

.page-full {
  height: calc(100vh - 64px);
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
}

.result-statics {
  justify-self: center;
  padding-top: 24px;
  min-width: 400px;
  text-align: center;
}

.chart-title {
  padding-top: 48px;
  padding-bottom: 4px;
  font-size: 24px;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.page-content {
  flex-grow: 1;
  margin-bottom: 48px;
  align-items: flex-end;
}

.page-button {
  width: 160px;
  height: 240px;
  margin-left: 12px;
  margin-right: 12px;
}

.page-button-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-button-icon {
  font-size: 52px;
  margin-bottom: 56px;
}

.page-button-text {
  font-size: 18px;
  margin-bottom: 4px;
  font-weight: bold;
  letter-spacing: 0.12em;
}

.chart-container {
  width: 800px;
  margin: auto;
  align-items: flex-end;
}
</style>
