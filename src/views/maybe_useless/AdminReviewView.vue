<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import dayjs from 'dayjs'
import axios from "axios";
import {useRouter} from "vue-router";
import {ElNotification} from "element-plus";

const ReviewData = ref([])

const reviewTarget = ref("无标题")
const avgRating = ref(0.0)
const router = useRouter()

const reloadData = async () => {
  await axios.get("/reviews/" + router.currentRoute.value.query.type + "/" +
                  router.currentRoute.value.query.id)
      .then((response) => {
        let sum: number = 0
        ReviewData.value = response.data['Reviews']
            .map((review: {ReviewID: number, Rating: number, Comment: string, CreatedAt: Date, UserID: number, UserName: string}) => {
              sum += review.Rating
              return (
                {
                  userId: review.UserID,
                  username: review.UserName,
                  reviewId: review.ReviewID,
                  rating: review.Rating,
                  time: dayjs(review.CreatedAt).utc().format('YYYY-MM-DD HH:mm:ss'),
                  content: review.Comment,
                }
            )})
        avgRating.value = ReviewData.value.length === 0 ? 0.0 : sum / ReviewData.value.length
        reviewTarget.value = response.data['ContentName']
      })
      .catch((error) => {
        console.error(error)
        ElNotification({
          title: '出现错误，请重试',
          type: "error",
        })
      })
}

const formatScore = (value: number) => { return `${value.toFixed(1)} 分` }

onMounted(async () => {
  await reloadData()
})

</script>

<template>
  <el-container class="admin-container">
    <el-header class="review-target">{{ reviewTarget }}</el-header>
    <el-rate v-model="avgRating" class="review-rate" disabled :score-template="formatScore(avgRating)" show-score
             text-color="#ff9900"/>
    <el-main>
      <el-table :data="ReviewData" class="admin-table" stripe>
        <el-table-column label="评论id" prop="reviewId" width="100"/>
        <el-table-column label="用户id" prop="userId" width="100"/>
        <el-table-column label="用户名" prop="username" width="200"/>
        <el-table-column label="评分" prop="rating" width="250">
          <template #default="scope">
            <el-rate v-model="scope.row.rating" disabled score-template="{value} 分" show-score
                     text-color="#ff9900"/>
          </template>
        </el-table-column>
        <el-table-column label="评论" prop="content" min-width="200"/>
        <el-table-column label="发布时间" prop="time" width="200"/>
      </el-table>
    </el-main>
  </el-container>

</template>

<style scoped>

.review-target {
  font-size: 2rem;
}

.review-rate {
  margin: -10px 0 0 18px;
}

.admin-container {
  display: flex;
  justify-content: left;
  align-items: flex-start;
  padding: 20px 20px 0 20px;
}

.admin-table {
  height: calc(100vh - 214px);
  width: calc(100vw - 80px);
}
</style>
