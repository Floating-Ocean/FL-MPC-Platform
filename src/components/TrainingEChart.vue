<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch} from 'vue'
import * as echarts from 'echarts'
import { ElContainer } from 'element-plus'

const chartEl = ref<HTMLElement>()
let chart: echarts.ECharts

// 使用 ref 使数据响应式，并通过 computed 生成动态轮次
const accData = ref<number[]>([])
const lossData = ref<number[]>([])
const epochs = computed(() =>
  Array.from({ length: lossData.value.length }, (_, i) => `第${i + 1}轮`)
)

// 暴露数据给父组件
defineExpose({
  accData,
  lossData
})

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
      data: epochs.value, // 使用计算属性
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
        data: accData.value, // 使用 ref 值
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
        data: lossData.value, // 使用 ref 值
      },
    ],
  }

  chart.setOption(option)
}

// 监听数据变化自动更新图表
watch([accData, lossData], () => {
  if (chart) {
    chart.setOption({
      xAxis: { data: epochs.value },
      series: [
        { data: accData.value },
        { data: lossData.value }
      ]
    })
  }
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  if (chart) chart.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})
</script>

<template>
  <el-container>
    <div class="chart-container">
      <div ref="chartEl" style="height: 300px"></div>
    </div>
  </el-container>
</template>

<style scoped>
.chart-container {
  width: 700px;
  margin: auto;
  align-items: flex-end;
}
</style>
