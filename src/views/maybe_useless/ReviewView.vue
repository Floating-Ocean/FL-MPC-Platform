<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {useRouter} from "vue-router";
import axios from 'axios';
import {ArrowRight} from '@element-plus/icons-vue'

interface BookForm {
  id: number;
  title: string;
  author: string;
  genre: string;
  publication_year: string;
  isbn: string;
}

interface MovieForm {
  id: number;
  title: string;
  director: string;
  genre: string;
  release_year: string;
  duration: string;
}

interface MusicForm {
  id: number;
  title: string;
  artist: string;
  album: string;
  release_year: string;
  genre: string;
}

const router = useRouter()

const BookData = ref<BookForm[]>([])
const MovieData = ref<MovieForm[]>([])
const MusicData = ref<MusicForm[]>([])

const reloadData = async () => {
  await axios.get('/data')
      .then(response => {
        BookData.value = response.data['books']
            .map((book: {
              BookID: number,
              Title: string,
              Author: string,
              Genre: string,
              PublicationYear: number,
              ISBN: string
            }) => (
                {
                  id: book.BookID,
                  title: book.Title,
                  author: book.Author,
                  genre: book.Genre,
                  publication_year: book.PublicationYear.toString(),
                  isbn: book.ISBN,
                }
            ))
        MovieData.value = response.data['movies']
            .map((movie: {
              MovieID: number
              Title: string,
              Director: string,
              Genre: string,
              ReleaseYear: number,
              Duration: number
            }) => (
                {
                  id: movie.MovieID,
                  title: movie.Title,
                  director: movie.Director,
                  genre: movie.Genre,
                  release_year: movie.ReleaseYear.toString(),
                  duration: movie.Duration.toString(),
                }
            ))
        MusicData.value = response.data['music']
            .map((music: {
              MusicID: number,
              Title: string,
              Artist: string,
              Album: string,
              ReleaseYear: number,
              Genre: string
            }) => (
                {
                  id: music.MusicID,
                  title: music.Title,
                  artist: music.Artist,
                  album: music.Album,
                  release_year: music.ReleaseYear.toString(),
                  genre: music.Genre,
                }
            ))
      })
      .catch(() => {
        alert("权限不足，请先登录")
        router.push('/login')
      })
};

onMounted(async () => {
  await reloadData();
})

const toComment = (type: string, id: number) => {
  router.push({
    path: '/review/detail',
    query: {
      type: type,
      id: id
    }
  })
}

</script>

<template>
  <el-tabs class="review-category-tabs">
    <el-tab-pane label="书籍">
      <el-container class="review-container">
        <el-row v-for="bookData in BookData" :key="bookData.id" class="review-item">
          <el-col :span="18">
            <el-descriptions :title="bookData.title" class="review-item-descriptions">
              <el-descriptions-item label="书名">{{ bookData.title }}</el-descriptions-item>
              <el-descriptions-item label="作者">{{ bookData.author }}</el-descriptions-item>
              <el-descriptions-item label="流派">{{ bookData.genre }}</el-descriptions-item>
              <el-descriptions-item label="出版年份">{{ bookData.publication_year }}</el-descriptions-item>
              <el-descriptions-item label="ISBN">{{ bookData.isbn }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="6" class="review-action-group">
            <el-button class="review-action" plain round size="large" type="primary"
                       @click.prevent="toComment('Book', bookData.id)">
              看看大家的评论
              <el-icon class="el-icon--right">
                <ArrowRight/>
              </el-icon>
            </el-button>
          </el-col>
        </el-row>
      </el-container>
    </el-tab-pane>
    <el-tab-pane label="电影">
      <el-container class="review-container">
        <el-row v-for="movieData in MovieData" :key="movieData.id" class="review-item">
          <el-col :span="18">
            <el-descriptions :title="movieData.title" class="review-item-descriptions">
              <el-descriptions-item label="片名">{{ movieData.title }}</el-descriptions-item>
              <el-descriptions-item label="导演">{{ movieData.director }}</el-descriptions-item>
              <el-descriptions-item label="分类">{{ movieData.genre }}</el-descriptions-item>
              <el-descriptions-item label="上映年份">{{ movieData.release_year }}</el-descriptions-item>
              <el-descriptions-item label="影片时长">{{ movieData.duration }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="6" class="review-action-group">
            <el-button class="review-action" plain round size="large" type="primary"
                       @click.prevent="toComment('Movie', movieData.id)">
              看看大家的评论
              <el-icon class="el-icon--right">
                <ArrowRight/>
              </el-icon>
            </el-button>
          </el-col>
        </el-row>
      </el-container>
    </el-tab-pane>
    <el-tab-pane label="音乐">
      <el-container class="review-container">
        <el-row v-for="musicData in MusicData" :key="musicData.id" class="review-item">
          <el-col :span="18">
            <el-descriptions :title="musicData.title" class="review-item-descriptions">
              <el-descriptions-item label="曲名">{{ musicData.title }}</el-descriptions-item>
              <el-descriptions-item label="艺术家">{{ musicData.artist }}</el-descriptions-item>
              <el-descriptions-item label="专辑">{{ musicData.album }}</el-descriptions-item>
              <el-descriptions-item label="发行年份">{{ musicData.release_year }}</el-descriptions-item>
              <el-descriptions-item label="曲风">{{ musicData.genre }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="6" class="review-action-group">
            <el-button class="review-action" plain round size="large" type="primary"
                       @click.prevent="toComment('Music', musicData.id)">
              看看大家的评论
              <el-icon class="el-icon--right">
                <ArrowRight/>
              </el-icon>
            </el-button>
          </el-col>
        </el-row>
      </el-container>
    </el-tab-pane>
  </el-tabs>

</template>

<style scoped>

.review-container {
  flex-direction: column;
  padding: 20px;
  background-color: var(--color-background-mute);
  height: calc(100vh - 104px);
  overflow-y: auto;
}

.review-header {
  font-size: 2rem;
}

.review-table {
  height: calc(100vh - 234px);
  width: calc(100vw - 120px);
}

.review-action-group {
  margin: -16px -24px -24px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.review-action {
  opacity: 0;
}

.review-item {
  background-color: var(--color-background);
  padding: 16px 24px 24px 24px;
  margin-bottom: 20px;
  border-radius: 16px;
  box-shadow: 4px 8px 24px 0 rgba(0, 0, 0, 0.06);
  transition: background-color 0.1s;
}

.review-item-descriptions {
  margin-bottom: -10px;
}

.review-item:hover {
  background-color: var(--el-table-row-hover-bg-color);

  .review-action {
    opacity: 1;
  }
}
</style>


<style>
.review-category-tabs {
  .el-tabs__nav.is-top {
    padding: 0 26px;
  }

  .el-tabs__header.is-top {
    margin: 0;
  }
}

.review-item-descriptions {
  .el-descriptions__title {
    font-size: 28px;
  }

  .el-descriptions__label {
    font-weight: 500;
  }

  .el-descriptions__body {
    background-color: transparent;
  }
}
</style>
