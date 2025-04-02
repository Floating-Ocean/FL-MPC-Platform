<script lang="ts" setup>
import {RouterView, useRouter} from 'vue-router'
import {ElNotification, ElPageHeader} from 'element-plus'
import {User} from '@element-plus/icons-vue'
import axios from "axios";
import {isLoggedIn, userName} from "@/router";

const router = useRouter()

const onBack = () => {
  window.history.back()
}

const logout = async () => {
  await axios.post('/logout')
      .then(() => {
        router.push('/')
        window.location.reload()
      })
      .catch((error) => {
        console.error(error)
        ElNotification({
          title: '出现错误，请重试',
          type: "error",
        })
      })
}

const toHome = () => {
  router.push('/')
}

</script>

<template>
  <div class="container">
    <el-page-header @back="onBack" class="app-header">
      <template #content>
        <span class="text-large font-600 mr-3" @click="toHome" style="cursor:pointer;"> 面向隐私保护的联邦学习框架 </span>
        <span class="text-sm mr-2" style="color: var(--el-text-color-regular)">
          {{ $route.meta.title }}
        </span>
      </template>
      <template #extra>
        <el-popconfirm title="退出登录?" @confirm="logout">
        <template #reference>
          <el-button v-if="isLoggedIn" class="app-user" text>
            <el-icon class="app-user-icon"><User/></el-icon>
            <span class="app-user-name">{{ userName }}</span>
          </el-button>
        </template>
      </el-popconfirm>
      </template>
    </el-page-header>
    <RouterView/>
  </div>
</template>

<style scoped>
.container {
  height: 100%;
  width: 100%;
}

.app-header {
  padding: 16px 24px;
  background-color: var(--color-background);
  height: 64px;
  align-content: center;
}

.app-user {
  margin-right: 24px;
}

</style>
