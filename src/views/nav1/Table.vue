<template>
<section>
		<!--列表-->
		<el-table :data="userList" highlight-current-row style="width: 100%;">
			<el-table-column type="index" width="60">
			</el-table-column>
      <el-table-column prop="id"  label="id" width="140" sortable>
			</el-table-column>
			<el-table-column prop="name" label="昵称" width="120" sortable>
			</el-table-column>
      <el-table-column prop="gender" label="性别" width="120" sortable>
			</el-table-column>
      <el-table-column prop="description" label="描述" width="200" sortable>
			</el-table-column>
      <el-table-column prop="fans_count" label="粉丝数" width="170" sortable>
			</el-table-column>
      <el-table-column prop="follows_count" label="关注数" width="90" sortable>
			</el-table-column>
			<el-table-column prop="weibos_count" label="微博数" width="90" sortable>
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
      userList: '',
      tableDataName: '',
      tableDataEnd: '',
      filterTableDataEnd: '',
      flag: 0
    };
  },
  created() {
    this.getUsers()
  },
  methods: {
    getUsers() {
      const path = 'http://127.0.0.1:5000/api/users/listpage'
      axios.get(path)
        .then((res) => {
          console.log(res.data.infos);
          this.userList = res.data.infos
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
        this.currentChangePage(this.userList, currentPage)
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
      this.total1 = this.userList.length
      this.flag = 0
      this.handleCurrentChange1(this.currentPage1)
    }
  }
}

</script>

<style scoped>

</style>