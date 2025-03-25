<script lang="ts" setup>
import { Guide, Coin, Upload } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElButton } from 'element-plus'

const router = useRouter()

const training = false


const goTrain = () => {
  router.push('/start/param')
}

const goStatus = () => {
  router.push('/train')
}

</script>

<template>
  <el-container class="page-container">
      <el-row>
        <el-text class="page-title">该从哪里开始呢</el-text>
      </el-row>
      <el-row class="page-content">
        <el-button v-if="!training" type="primary" class="page-button" round
                   @click="goTrain">
          <div class="page-button-content">
            <el-icon class="page-button-icon"><Guide /></el-icon>
            <span class="page-button-text">训练新模型</span>
          </div>
        </el-button>
        <el-button v-else type="warning" class="page-button" round
                   @click="goStatus">
          <div class="page-button-content">
            <el-icon class="page-button-icon"><Coin /></el-icon>
            <span class="page-button-text">查看训练状态</span>
          </div>
        </el-button>
        <el-upload
          ref="uploader"
          :http-request="handleBeforeUpload"
          accept=".pth">
          <el-button class="page-button" round>
            <div class="page-button-content">
              <el-icon class="page-button-icon"><Upload /></el-icon>
              <span class="page-button-text">上传已有模型</span>
            </div>
          </el-button>
        </el-upload>

      </el-row>
    </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 24px;
}

.page-title{
  font-size: 48px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.page-content{
  margin-top: 64px;
  margin-bottom: 24px;
}

.page-button {
  width: 160px;
  height: 240px;
  margin-left: 12px;
  margin-right: 12px;
}

.page-button-content{
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
</style>
