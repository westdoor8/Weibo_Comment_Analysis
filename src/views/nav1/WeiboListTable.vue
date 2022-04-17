<template>
<section>
		<!--列表-->
		<el-table
        :data="weiboList"
        highlight-current-row
        style="width: 100%;"

    >
			<el-table-column type="index" width="60">
			</el-table-column>
      <el-table-column prop="id"  label="id" width="140" sortable>
			</el-table-column>
			<el-table-column prop="bid" label="bid" width="140" sortable>
			</el-table-column>
      <el-table-column prop="user_id" label="user_id" width="120" sortable>
			</el-table-column>
      <el-table-column prop="screen_name" label="screen_name" width="120" sortable>
			</el-table-column>
      <el-table-column prop="text" label="text" width="400" sortable>
			</el-table-column>
      <el-table-column prop="at_users" label="at_users" width="90" sortable>
			</el-table-column>
      <el-table-column prop="location" label="location" width="170" sortable>
			</el-table-column>
			<el-table-column prop="created_at" label="created_at" width="90" sortable>
			</el-table-column>
      <el-table-column prop="full_created_at" label="full_created_at" width="170" sortable>
			</el-table-column>
      <el-table-column prop="source" label="source" width="170" sortable>
			</el-table-column>
      <el-table-column prop="attitudes_count" label="attitudes_count" width="170" sortable>
			</el-table-column>
      <el-table-column prop="attitudes_count" label="点赞数" width="170" sortable>
			</el-table-column>
      <el-table-column prop="comments_count" label="评论数" width="170" sortable>
			</el-table-column>
      <el-table-column prop="reposts_count" label="转发数" width="170" sortable>
			</el-table-column>
		</el-table>
  <el-pagination
        :current-page="currentPage1"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        :total="total1"
        @size-change="handleSizeChange1"
        @current-change="handleCurrentChange1"
      />
</section>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      total1: 10,
      currentPage1: 1,
      pageSize: 10,
      weiboList: '',
      tableDataName: '',
      tableDataEnd: '',
      filterTableDataEnd: '',
      flag: 0
    };
  },
  created() {
    this.getWeibos()
  },
  methods: {
    getWeibos() {
      const path = 'http://127.0.0.1:5000/api/weibos/listpage'
      axios.get(path)
        .then((res) => {
          this.weiboList = res.data.infos
          this.getCreateTable()
        })
        .catch((error) => {
          alert(error)
      })
    },
    handleSizeChange1: function(pageSize) { // 每页条数切换
      // eslint-disable-next-line eqeqeq
      if (this.flag == 1) {
        return
      }
      this.pageSize = pageSize
      this.handleCurrentChange1(this.currentPage1)
    },
    handleCurrentChange1: function(currentPage) { // 页码切换
      this.currentPage1 = currentPage
      // eslint-disable-next-line eqeqeq
      if (this.flag == 0) {
        this.currentChangePage(this.weiboList, currentPage)
      } else {
        this.currentChangePage(this.filterTableDataEnd, currentPage)
      }
    },
    // 分页方法（重点）
    currentChangePage(list, currentPage) {
      let from = (currentPage - 1) * this.pageSize
      this.tempList = []
      const to = currentPage * this.pageSize
      for (; from < to; from++) {
        if (list[from]) {
          this.tempList.push(list[from])
        }
      }
    },
    getCreateTable() {
      this.total1 = this.weiboList.length
      this.flag = 0
      this.handleCurrentChange1(this.currentPage1)
    },
    openData(){
      this.tableDataName = []
      this.getCreateTable()
    }
  }
}

</script>

<style scoped>

</style>