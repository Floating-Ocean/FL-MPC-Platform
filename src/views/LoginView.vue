<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from "vue-router";
import axios from 'axios';
import {ElNotification} from "element-plus";

interface LoginForm {
  username: string;
  password: string;
}

const loginForm = ref<LoginForm>({username: '', password: '',})
const loginRules = ref({
  username: [{required: true, message: '请输入用户名', trigger: 'blur'},],
  password: [{required: true, message: '请输入密码', trigger: 'blur'},],
})
const loginFormRef = ref()
const router = useRouter()
const submitForm = () => {
  if (loginFormRef.value) {
    loginFormRef.value.validate(async (valid: boolean) => {
      if (valid) {
        await axios.post("/login", loginForm.value)
            .then(() => {
              ElNotification({
                title: '登陆成功',
                type: "success",
              })
              router.push('/review')
            })
            .catch(error => {
              console.error(error)
              ElNotification({
                title: '用户名或密码错误',
                type: "error",
              })
            })
      } else {
        ElNotification({
          title: '输入不合法',
          type: "error",
        })
        return false
      }
    })
  }
}
const goRegister = () => {
  router.push('/register')
}
</script>

<template>
  <el-container class="login-container">
    <el-header class="login-header">欢迎，请登录</el-header>
    <el-main>
      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" status-icon>
        <el-form-item class="login-from-item" label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"
                    size="large"></el-input>
        </el-form-item>
        <el-form-item class="login-from-item" label="密码" prop="password">
          <el-input v-model="loginForm.password" placeholder="请输入密码" size="large"
                    type="password"></el-input>
        </el-form-item>
        <el-form-item class="login-actions">
          <el-button size="large" type="primary" @click="submitForm">登录</el-button>
          <el-button size="large" @click="goRegister">注册</el-button>
        </el-form-item>
      </el-form>
    </el-main>
  </el-container>
</template>

<style scoped>

.login-container {
  display: flex;
  justify-content: left;
  align-items: flex-start;
  padding: 36px;
  background: var(--color-background-mute);
  height: calc(100vh - 64px);
}

.login-header {
  font-size: 2rem;
}

.login-from-item {
  flex-direction: column;
  align-items: flex-start;
}

.login-from-item .el-input {
  width: 40vw;
}

.login-actions {
  padding-top: 28px;
}
</style>
