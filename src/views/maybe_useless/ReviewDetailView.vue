<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import dayjs from 'dayjs'
import {Edit} from '@element-plus/icons-vue'
import {useRouter} from "vue-router";
import axios from "axios";
import {ElNotification} from "element-plus";

interface ReviewDetail {
  userID: number;
  reviewId: number;
  username: string;
  time: string;
  rating: number;
  content: string;
}

const ReviewDetailData = ref<ReviewDetail[]>([])
const dialogAddVisible = ref(false)

interface AddReviewDetailForm {
  rating: number;
  content: string;
}

const addReviewDetailForm = ref<AddReviewDetailForm>({rating: 0, content: '',})
const addReviewDetailRules = ref({
  rating: [{required: true, message: '请输入评分', trigger: 'blur'},],
  content: [{required: true, message: '请输入评论', trigger: 'blur'},],
})
const addReviewDetailFormRef = ref()
const router = useRouter()
const submitForm = () => {
  if (addReviewDetailFormRef.value) {
    addReviewDetailFormRef.value.validate(async (valid: boolean) => {
      if (valid) {
        await axios.post('/add_review', {
          content_type: router.currentRoute.value.query.type,
          content_id: router.currentRoute.value.query.id,
          rating: addReviewDetailForm.value.rating,
          comment: addReviewDetailForm.value.content,
        })
        addReviewDetailForm.value = {rating: 0, content: '',}
        ElNotification({
          title: '发表成功',
          type: "success",
        })
        dialogAddVisible.value = false
        await reloadData()
      } else {
        console.log('输入不合法')
        return false
      }
    })
  }
}

const reviewDetailTarget = ref("无标题")
const avgRating = ref(0.0)

const addReviewDetail = () => {
  dialogAddVisible.value = true
}

const currentSession = ref({})

const fetchSession = async () => {
  await axios.get("/current_session")
      .then((response) => currentSession.value = response.data)
      .catch((error) => {
        console.error(error)
        ElNotification({
          title: '出现错误，请重试',
          type: "error",
        })
      })
}

const reloadData = async () => {
  await axios.get("/reviews/" + router.currentRoute.value.query.type + "/" +
      router.currentRoute.value.query.id)
      .then((response) => {
        let sum: number = 0
        ReviewDetailData.value = response.data['Reviews']
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
        avgRating.value = ReviewDetailData.value.length === 0 ? 0.0 : sum / ReviewDetailData.value.length
        reviewDetailTarget.value = response.data['ContentName']
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
  await fetchSession()
  await reloadData()
})

</script>

<template>
  <el-container class="review-detail-container">
    <el-header class="review-detail-target">{{ reviewDetailTarget }}</el-header>
    <el-rate v-model="avgRating" class="review-detail-rate" disabled :score-template="formatScore(avgRating)" show-score
             text-color="#ff9900"/>
    <div class="review-detail-items">
      <div v-for="reviewDetail in ReviewDetailData" :key="reviewDetail.time" class="review-detail-item">
        <div class="review-detail-header">
          <span class="review-detail-username">{{ reviewDetail.username }}</span>
          <el-rate v-model="reviewDetail.rating" class="review-detail-rating" disabled></el-rate>
          <span class="review-detail-time">{{ reviewDetail.time }}</span>
        </div>
        <div class="review-detail-content">{{ reviewDetail.content }}</div>
      </div>
      <el-affix :offset="24" position="bottom" style="text-align: center; padding-top: 12px">
        <el-button :icon="Edit" class="floating-button" size="large" type="primary"
                   @click="addReviewDetail">
          发表一条我的评论
        </el-button>
      </el-affix>
    </div>
    <el-dialog v-model="dialogAddVisible" title="发表评论" width="500">
      <el-form ref="addReviewDetailFormRef" :model="addReviewDetailForm" :rules="addReviewDetailRules" status-icon>
        <el-form-item class="add-review-detail-from-item" label="评分" prop="rating">
          <el-rate v-model="addReviewDetailForm.rating" :score-template="formatScore(addReviewDetailForm.rating)" show-score
                   text-color="#ff9900"/>
        </el-form-item>
        <el-form-item class="add-review-detail-from-item" label="评论" prop="content">
          <el-input v-model="addReviewDetailForm.content" placeholder="请输入评论内容" type="textarea"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogAddVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">继续</el-button>
        </div>
      </template>
    </el-dialog>
  </el-container>
</template>

<style scoped>

.floating-button {
  box-shadow: 4px 8px 24px 0 rgba(0, 0, 0, 0.06);
}

.review-detail-items{
  padding: 20px;
}

.review-detail-target {
  font-size: 2rem;
}

.review-detail-rate {
  margin: -10px 0 0 18px;
}

.review-detail-container {
  padding: 20px;
  background-color: var(--color-background-mute);
  height: calc(100vh - 64px);
  overflow-y: auto;
}

.review-detail-item {
  background-color: var(--color-background);
  padding: 16px 24px 24px 24px;
  margin-bottom: 20px;
  border-radius: 16px;
  box-shadow: 4px 8px 24px 0 rgba(0, 0, 0, 0.06);
}

.review-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.review-detail-username {
  font-weight: bold;
  font-size: 16px;
}

.review-detail-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.review-detail-content {
  font-size: 14px;
}

.review-detail-rating {
  margin-left: 10px;
}
</style>
