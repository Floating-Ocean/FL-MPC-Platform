<script lang="ts" setup>
import { ArrowRightBold } from '@element-plus/icons-vue'
import axios from "axios";
import {useRouter} from "vue-router";

const router = useRouter()

const onNext = async () => {
  await axios.get('/current_session')
      .then(() => {
          router.push('/start')
      })
      .catch(() => {
          router.push('/login')
      })
}

</script>

<template>
  <main class="page-container">
    <el-text class="page-title">面向隐私保护的联邦学习框架</el-text>
    <el-text class="home-subtitle">基于 联邦学习 · 秘密共享 · 隐私保护 的机器学习框架　 　 　　　　 　　数据安全实训大作业</el-text>
    <el-text class="home-author">&lt;&lt;　组员 · 夏子洋 · 项雍灿 · 王煜杰　&gt;&gt;</el-text>
    <el-button type="primary" :icon="ArrowRightBold" large class="home-next"
               @click="onNext"/>
  </main>
</template>

<style scoped>
.page-container{
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
}

.home-subtitle{
  letter-spacing: 0.062rem;
}

.home-author{
  letter-spacing: 0.1rem;
  padding-top: 6px;
}

.home-next{
  width: 64px;
  height: 64px;
  border-radius: 50%;
  font-size: 22px;
  margin-top: 64px;
}
</style>
