<script lang="ts" setup>
import { ref } from 'vue'
import {RouterView, useRouter} from 'vue-router'
import {ElNotification, ElPageHeader} from 'element-plus'
import {User} from '@element-plus/icons-vue'
import axios from "axios";
import {isLoggedIn, userName} from "@/router";

const router = useRouter()
const dialogVisible = ref<boolean>(false);

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

const handleCommand = (command: string | number | object) => {
  if (command === 'logout') {
    dialogVisible.value = true
  }else if(command == 'status'){
    toStatus()
  }else if(command == 'test'){
    toTest()
  }
}

const toHome = () => {
  router.push('/')
}

const toStatus = () => {
  router.push('/train')
}

const toTest = () => {
  router.push('/test')
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
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button v-if="isLoggedIn" class="app-user" text>
            <el-icon class="app-user-icon"><User/></el-icon>
            <span class="app-user-name">{{ userName }}</span>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="status">查看训练进度　　　　　</el-dropdown-item>
              <el-dropdown-item command="test">测试模型</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </el-page-header>
    <el-dialog
      v-model="dialogVisible"
      title="退出登录"
      width="500">
      <span>真的要退出登录吗？</span>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="dialogVisible = false; logout()">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
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
