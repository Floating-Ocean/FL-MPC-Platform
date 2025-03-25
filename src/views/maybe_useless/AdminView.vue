<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {useRouter} from "vue-router";
import axios from 'axios';
import {ElNotification} from "element-plus";


const dialogBookVisible = ref(false)
const dialogMovieVisible = ref(false)
const dialogMusicVisible = ref(false)
const dialogType = ref("添加新")

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

const bookForm = ref<BookForm>({id: 0, title: '', author: '', genre: '', publication_year: '', isbn: ''});
const movieForm = ref<MovieForm>({id: 0, title: '', director: '', genre: '', release_year: '', duration: ''});
const musicForm = ref<MusicForm>({id: 0, title: '', artist: '', album: '', release_year: '', genre: ''});

const validateYear = (rule: never, value: string, callback: (error?: Error) => void) => {
  const yearPattern = /^(19|20)\d{2}$/;
  if (!yearPattern.test(value)) {
    callback(new Error('请输入有效的年份'));
  } else {
    callback();
  }
};

const validateInteger = (rule: never, value: string, callback: (error?: Error) => void) => {
  if (!Number.isInteger(Number(value))) {
    callback(new Error('请输入整数'));
  } else {
    callback();
  }
};

const bookRules = ref({
  title: [{required: true, message: '请输入书名', trigger: 'blur'},],
  author: [{required: true, message: '请输入作者', trigger: 'blur'},],
  genre: [{required: true, message: '请输入流派', trigger: 'blur'},],
  publication_year: [{required: true, message: '请输入出版年份', trigger: 'blur'},
    {validator: validateYear, trigger: 'blur'},],
  isbn: [{required: true, message: '请输入ISBN', trigger: 'blur'},],
});

const movieRules = ref({
  title: [{required: true, message: '请输入片名', trigger: 'blur'},],
  director: [{required: true, message: '请输入导演', trigger: 'blur'},],
  genre: [{required: true, message: '请输入分类', trigger: 'blur'},],
  release_year: [{required: true, message: '请输入上映年份', trigger: 'blur'},
    {validator: validateYear, trigger: 'blur'},],
  duration: [{required: true, message: '请输入影片时长', trigger: 'blur'},
    {validator: validateInteger, trigger: 'blur'},],
});

const musicRules = ref({
  title: [{required: true, message: '请输入曲名', trigger: 'blur'},],
  artist: [{required: true, message: '请输入艺术家', trigger: 'blur'},],
  album: [{required: true, message: '请输入专辑', trigger: 'blur'},],
  release_year: [{required: true, message: '请输入发行年份', trigger: 'blur'},
    {validator: validateYear, trigger: 'blur'},],
  genre: [{required: true, message: '请输入曲风', trigger: 'blur'},],
});

const bookFormRef = ref()
const movieFormRef = ref()
const musicFormRef = ref()
const router = useRouter()

const submitBookForm = () => {
  if (bookFormRef.value) {
    bookFormRef.value.validate(async (valid: boolean) => {
      if (valid) {
        const data = {
          Title: bookForm.value.title,
          Author: bookForm.value.author,
          Genre: bookForm.value.genre,
          PublicationYear: parseInt(bookForm.value.publication_year),
          ISBN: bookForm.value.isbn,
        }
        if (dialogType.value === "添加新"){
          await axios.put('/add_book', data)
              .then(async () => {
                dialogBookVisible.value = false
                ElNotification({
                  title: '添加成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        }else{
          await axios.put('/edit_book', { ...data, BookID: bookForm.value.id })
              .then(async () => {
                dialogBookVisible.value = false
                ElNotification({
                  title: '修改成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        }
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
const submitMovieForm = () => {
  if (movieFormRef.value) {
    movieFormRef.value.validate(async (valid: boolean) => {
      if (valid) {
        const data = {
          Title: movieForm.value.title,
          Director: movieForm.value.director,
          Genre: movieForm.value.genre,
          ReleaseYear: parseInt(movieForm.value.release_year),
          Duration: parseInt(movieForm.value.duration),
        }
        if (dialogType.value === "添加新") {
          await axios.put('/add_movie', data)
              .then(async () => {
                dialogMovieVisible.value = false
                ElNotification({
                  title: '添加成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        } else {
          await axios.put('/edit_movie', { ...data, MovieID: movieForm.value.id })
              .then(async () => {
                dialogMovieVisible.value = false
                ElNotification({
                  title: '修改成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        }
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

const submitMusicForm = () => {
  if (musicFormRef.value) {
    musicFormRef.value.validate(async (valid: boolean) => {
      if (valid) {
        const data = {
          Title: musicForm.value.title,
          Artist: musicForm.value.artist,
          Album: musicForm.value.album,
          ReleaseYear: parseInt(musicForm.value.release_year),
          Genre: musicForm.value.genre,
        }
        if (dialogType.value === "添加新") {
          await axios.put('/add_music', data)
              .then(async () => {
                dialogMusicVisible.value = false
                ElNotification({
                  title: '添加成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        } else {
          await axios.put('/edit_music', { ...data, MusicID: musicForm.value.id })
              .then(async () => {
                dialogMusicVisible.value = false
                ElNotification({
                  title: '修改成功',
                  type: "success",
                })
                await reloadData()
              })
              .catch(error => {
                console.error(error)
                ElNotification({
                  title: '出现错误，请重试',
                  type: "error",
                })
              })
        }
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

const BookData = ref<BookForm[]>([])
const MovieData = ref<MovieForm[]>([])
const MusicData = ref<MusicForm[]>([])

const reloadData = async () => {
  await axios.get('/data')
      .then(response => {
        BookData.value = response.data['books']
            .map((book: { BookID: number, Title: string, Author: string, Genre: string, PublicationYear: number, ISBN: string }) => (
                {
                  id: book.BookID,
                  title: book.Title,
                  author: book.Author,
                  genre: book.Genre,
                  publication_year: book.PublicationYear.toString(),
                  isbn: book.ISBN
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
                  duration: movie.Duration.toString()
                }
            ))
        MusicData.value = response.data['music']
            .map((music: { MusicID: number, Title: string, Artist: string, Album: string, ReleaseYear: number, Genre: string }) => (
                {
                  id: music.MusicID,
                  title: music.Title,
                  artist: music.Artist,
                  album: music.Album,
                  release_year: music.ReleaseYear.toString(),
                  genre: music.Genre
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

const commentRow = (scope: string, index: number) => {
  switch (scope) {
    case 'Book':
      router.push({path: '/admin/review', query: {
          type: scope,
          id: BookData.value[index].id,
        }
      })
      break
    case 'Movie':
      router.push({path: '/admin/review', query: {
          type: scope,
          id: MovieData.value[index].id,
        }
      })
      break
    case 'Music':
      router.push({path: '/admin/review', query: {
          type: scope,
          id: MusicData.value[index].id,
        }
      })
      break
  }
}

const deleteRow = async (scope: string, index: number) => {
  switch (scope) {
    case 'Book':
      await axios.post('/delete_book', { BookID: BookData.value[index].id })
          .then(() => {
            ElNotification({
              title: '删除成功',
              type: "success",
            })
            BookData.value.splice(index, 1)
          })
          .catch(error => {
            console.error(error)
            ElNotification({
              title: '出现错误，请重试',
              type: "error",
            })
          })
      break
    case 'Movie':
      await axios.post('/delete_movie', { MovieID: MovieData.value[index].id })
          .then(() => {
            ElNotification({
              title: '删除成功',
              type: "success",
            })
            MovieData.value.splice(index, 1)
          })
          .catch(error => {
            console.error(error)
            ElNotification({
              title: '出现错误，请重试',
              type: "error",
            })
          })
      break
    case 'Music':
      await axios.post('/delete_music', { MusicID: MusicData.value[index].id })
          .then(() => {
            ElNotification({
              title: '删除成功',
              type: "success",
            })
            MusicData.value.splice(index, 1)
          })
          .catch(error => {
            console.error(error)
            ElNotification({
              title: '出现错误，请重试',
              type: "error",
            })
          })
      break
  }
}

const editRow = (scope: string, index: number) => {
  dialogType.value = "修改"
  switch (scope) {
    case 'Book':
      bookForm.value = JSON.parse(JSON.stringify(BookData.value[index]))
      dialogBookVisible.value = true
      break
    case 'Movie':
      movieForm.value = JSON.parse(JSON.stringify(MovieData.value[index]))
      dialogMovieVisible.value = true
      break
    case 'Music':
      musicForm.value = JSON.parse(JSON.stringify(MusicData.value[index]))
      dialogMusicVisible.value = true
      break
  }
}

const onAddItem = (scope: string) => {
  dialogType.value = "添加新"
  switch (scope) {
    case 'Book':
      bookForm.value = {id: 0, title: '', author: '', genre: '', publication_year: '', isbn: ''}
      dialogBookVisible.value = true
      break
    case 'Movie':
      movieForm.value = {id: 0, title: '', director: '', genre: '', release_year: '', duration: ''}
      dialogMovieVisible.value = true
      break
    case 'Music':
      musicForm.value = {id: 0, title: '', artist: '', album: '', release_year: '', genre: ''}
      dialogMusicVisible.value = true
      break
  }
}


</script>

<template>
  <el-dialog v-model="dialogBookVisible" :title="dialogType + '书籍'" width="500">
    <el-form ref="bookFormRef" :model="bookForm" :rules="bookRules" status-icon>
      <el-form-item class="admin-from-item" label="书名" label-width="80" prop="title">
        <el-input v-model="bookForm.title" placeholder="请输入书名"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="作者" label-width="80" prop="author">
        <el-input v-model="bookForm.author" placeholder="请输入作者"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="流派" label-width="80" prop="genre">
        <el-input v-model="bookForm.genre" placeholder="请输入流派"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="出版年份" label-width="80" prop="publication_year">
        <el-input v-model="bookForm.publication_year" placeholder="请输入出版年份"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="ISBN" label-width="80" prop="isbn">
        <el-input v-model="bookForm.isbn" placeholder="请输入ISBN"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogBookVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBookForm">继续</el-button>
      </div>
    </template>
  </el-dialog>
  <el-dialog v-model="dialogMovieVisible" :title="dialogType + '电影'" width="500">
    <el-form ref="movieFormRef" :model="movieForm" :rules="movieRules" status-icon>
      <el-form-item class="admin-from-item" label="片名" label-width="80" prop="title">
        <el-input v-model="movieForm.title" placeholder="请输入片名"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="导演" label-width="80" prop="director">
        <el-input v-model="movieForm.director" placeholder="请输入导演"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="分类" label-width="80" prop="genre">
        <el-input v-model="movieForm.genre" placeholder="请输入分类"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="上映年份" label-width="80" prop="release_year">
        <el-input v-model="movieForm.release_year" placeholder="请输入上映年份"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="影片时长" label-width="80" prop="duration">
        <el-input v-model="movieForm.duration" placeholder="请输入影片时长"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogMovieVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMovieForm">继续</el-button>
      </div>
    </template>
  </el-dialog>
  <el-dialog v-model="dialogMusicVisible" :title="dialogType + '音乐'" width="500">
    <el-form ref="musicFormRef" :model="musicForm" :rules="musicRules" status-icon>
      <el-form-item class="admin-from-item" label="曲名" label-width="80" prop="title">
        <el-input v-model="musicForm.title" placeholder="请输入曲名"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="艺术家" label-width="80" prop="artist">
        <el-input v-model="musicForm.artist" placeholder="请输入艺术家"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="专辑" label-width="80" prop="album">
        <el-input v-model="musicForm.album" placeholder="请输入专辑"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="发行年份" label-width="80" prop="release_year">
        <el-input v-model="musicForm.release_year" placeholder="请输入发行年份"></el-input>
      </el-form-item>
      <el-form-item class="admin-from-item" label="曲风" label-width="80" prop="genre">
        <el-input v-model="musicForm.genre" placeholder="请输入曲风"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogMusicVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMusicForm">继续</el-button>
      </div>
    </template>
  </el-dialog>

  <el-tabs class="admin-category-tabs" tab-position="left">
    <el-tab-pane label="书籍">
      <el-container class="admin-container">
        <el-header class="admin-header">书籍管理</el-header>
        <el-main>
          <el-table :data="BookData" class="admin-table" stripe>
            <el-table-column label="书名" prop="title" width="300"/>
            <el-table-column label="作者" prop="author" width="220"/>
            <el-table-column label="流派" prop="genre" width="200"/>
            <el-table-column label="出版年份" prop="publication_year" width="150"/>
            <el-table-column label="ISBN" prop="isbn" width="200"/>
            <el-table-column fixed="right" label="操作" min-width="180">
              <template #default="scope">
                <el-button link size="small" type="primary"
                           @click.prevent="commentRow('Book', scope.$index)">
                  查看评论
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="editRow('Book', scope.$index)">
                  修改
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="deleteRow('Book', scope.$index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button class="mt-4" size="large" style="width: 100%" @click="onAddItem('Book')">
            添加新书籍
          </el-button>
        </el-main>
      </el-container>
    </el-tab-pane>
    <el-tab-pane label="电影">
      <el-container class="admin-container">
        <el-header class="admin-header">电影管理</el-header>
        <el-main>
          <el-table :data="MovieData" class="admin-table" stripe>
            <el-table-column label="片名" prop="title" width="350"/>
            <el-table-column label="导演" prop="director" width="220"/>
            <el-table-column label="分类" prop="genre" width="200"/>
            <el-table-column label="上映年份" prop="release_year" width="150"/>
            <el-table-column label="影片时长" prop="duration" width="150"/>
            <el-table-column fixed="right" label="操作" min-width="180">
              <template #default="scope">
                <el-button link size="small" type="primary"
                           @click.prevent="commentRow('Movie', scope.$index)">
                  查看评论
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="editRow('Movie', scope.$index)">
                  修改
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="deleteRow('Movie', scope.$index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button class="mt-4" size="large" style="width: 100%" @click="onAddItem('Movie')">
            添加新影片
          </el-button>
        </el-main>
      </el-container>
    </el-tab-pane>
    <el-tab-pane label="音乐">
      <el-container class="admin-container">
        <el-header class="admin-header">音乐管理</el-header>
        <el-main>
          <el-table :data="MusicData" class="admin-table" stripe>
            <el-table-column label="曲名" prop="title" width="300"/>
            <el-table-column label="艺术家" prop="artist" width="220"/>
            <el-table-column label="专辑" prop="album" width="200"/>
            <el-table-column label="发行年份" prop="release_year" width="150"/>
            <el-table-column label="曲风" prop="genre" width="200"/>
            <el-table-column fixed="right" label="操作" min-width="180">
              <template #default="scope">
                <el-button link size="small" type="primary"
                           @click.prevent="commentRow('Music', scope.$index)">
                  查看评论
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="editRow('Music', scope.$index)">
                  修改
                </el-button>
                <el-button link size="small" type="primary"
                           @click.prevent="deleteRow('Music', scope.$index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button class="mt-4" size="large" style="width: 100%" @click="onAddItem('Music')">
            添加新曲目
          </el-button>
        </el-main>
      </el-container>
    </el-tab-pane>
  </el-tabs>

</template>

<style scoped>

.admin-container {
  display: flex;
  justify-content: left;
  align-items: flex-start;
}

.admin-header {
  font-size: 2rem;
}

.admin-category-tabs {
  height: calc(100vh - 80px);
  padding-top: 12px;
}

.admin-table {
  height: calc(100vh - 234px);
  width: calc(100vw - 120px);
}
</style>
