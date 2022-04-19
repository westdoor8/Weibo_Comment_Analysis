<template>
    <div>
        <div id="word-text-area">
            <el-input type="textarea" :rows="10" placeholder="请输入内容" v-model="textarea">
            </el-input>
            <div id="word-img">
                <el-image :src="'data:image/png;base64,'+pic" :fit="fit">
                    <div slot="error" class="image-slot">
                        <i class="el-icon-picture-outline"></i>
                    </div>
                </el-image>
                <img style="width: 750px; height: 500px" :src="imgUrl" alt="">
            </div>
            <div id="word-operation">
                <el-row>
                    <el-button type="primary" @click="getPic" round>生成词云</el-button>
                </el-row>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from "axios";

    export default {
        name: 'wordcloud',
        data() {
          return {
                imgUrl: require('../../../app/images/jinkou_comment.png'),
                textarea: '',
                pic: "",
                pageTitle: 'Flask Vue Word Cloud',
            }
        },
        methods: {
          getPic() {
            const path = 'http://127.0.0.1:5000/api/wordcloud/w2'
            axios.get(path)
              .then((res) => {
                this.pic = res.data
              })
              .catch((error) => {
                alert(error)
            })
          }
        }
    }
</script>