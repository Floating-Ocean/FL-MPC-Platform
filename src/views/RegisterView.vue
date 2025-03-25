<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import axios from "axios";
import {ElNotification} from "element-plus";

interface RegisterForm {
  username: string;
  password: string;
  confirm_passwd: string;
  email: string;
}

const validatePasswd = (rule: never, value: string, callback: (error?: Error) => void) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerForm = ref<RegisterForm>({username: '', password: '', confirm_passwd: '', email: ''})
const registerRules = ref({
  username: [{required: true, message: '请输入用户名', trigger: 'blur'},],
  password: [{required: true, message: '请输入密码', trigger: 'blur'},],
  confirm_passwd: [{required: true, message: '请再次输入密码', trigger: 'blur'},
    { validator: validatePasswd, trigger: ['blur', 'change'] },],
  email: [{required: true, message: '请输入邮箱', trigger: 'blur'},
    {type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change']},],
})
const registerFormRef = ref()
const router = useRouter()
const submitForm = () => {
  if (registerFormRef.value) {
    registerFormRef.value.validate(async (valid: boolean) => {
      console.log(111)
      if (valid) {
        await axios.post("/register", registerForm.value)
            .then(() => {
              ElNotification({
                title: '注册成功，请完成登录',
                type: "success",
              })
              router.push('/login')
            })
            .catch(error => {
              console.error(error)
              ElNotification({
                title: '注册失败，请联系管理员',
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
</script>

<template>
  <el-container class="register-container">
    <el-header class="register-header">注册账号</el-header>
    <el-main>
      <el-form ref="registerFormRef" :model="registerForm" :rules="registerRules" status-icon>
        <el-form-item class="register-from-item" label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"
                    size="large"></el-input>
        </el-form-item>
        <el-form-item class="register-from-item" label="密码" prop="password">
          <el-input v-model="registerForm.password" placeholder="请输入密码" size="large"
                    type="password"></el-input>
        </el-form-item>
        <el-form-item class="register-from-item" label="确认密码" prop="confirm_passwd">
          <el-input v-model="registerForm.confirm_passwd" placeholder="请再次输入密码" size="large"
                    type="password"></el-input>
        </el-form-item>
        <el-form-item class="register-from-item" label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"
                    size="large"></el-input>
        </el-form-item>
        <el-form-item class="register-actions">
          <el-button size="large" type="primary" @click="submitForm">注册</el-button>
        </el-form-item>
      </el-form>
    </el-main>
  </el-container>
</template>

<style scoped>

.register-container {
  display: flex;
  justify-content: left;
  align-items: flex-start;
  padding: 36px;
  background: var(--color-background-mute);
  height: calc(100vh - 64px);
}

.register-header {
  font-size: 2rem;
}

.register-from-item {
  flex-direction: column;
  align-items: flex-start;
}

.register-from-item .el-input {
  width: 40vw;
}

.register-actions {
  padding-top: 28px;
}
</style>
