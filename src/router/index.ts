import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import axios from "axios";
import {ref} from "vue";

export const isLoggedIn = ref<boolean>(false);
export const isAdmin = ref<boolean>(false);
export const userName = ref<string>('未登录');

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta:{
        title: '首页'
      },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta:{
        title: '登录'
      },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta:{
        title: '注册'
      },
    },
    {
      path: '/start',
      name: 'start',
      component: () => import('../views/StartView.vue'),
      meta:{
        requiresAuth: false,
        title: '开始'
      },
    },
    {
      path: '/start/param',
      name: 'param',
      component: () => import('../views/ParamView.vue'),
      meta:{
        requiresAuth: false,
        title: '配置'
      },
    },
    {
      path: '/train',
      name: 'train',
      component: () => import('../views/TrainView.vue'),
      meta:{
        requiresAuth: false,
        title: '训练'
      },
    },
    {
      path: '/train/finish',
      name: 'train_finish',
      component: () => import('../views/TrainFinishedView.vue'),
      meta:{
        requiresAuth: false,
        title: '训练完成'
      },
    },
    {
      path: '/test',
      name: 'test',
      component: () => import('../views/TestView.vue'),
      meta:{
        requiresAuth: false,
        title: '测试'
      },
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  await axios.get('/current_session')
      .then(response => {
        isLoggedIn.value = true
        isAdmin.value = response.data['isAdmin']
        userName.value = response.data['username']
        if(response.data['isAdmin'] !== true && to.matched.some(record => record.meta.requiresAdminAuth)) {
          alert("权限不足，请使用管理员账号登录")
          next('/login')
        }else {
          next()
        }
      })
      .catch(() => {
        isLoggedIn.value = false
        isAdmin.value = false
        userName.value = '未登录'
        if(to.matched.some(record => record.meta.requiresAuth)) {
          alert("请先登录")
          next('/login')
        }else{
          next()
        }
      })
})

export default router
