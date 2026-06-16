<!--
  文件：App.vue
  功能：根组件
  说明：应用的最顶层组件
-->

<template>
  <router-view />
</template>

<script setup>
/**
 * 根组件
 * 使用router-view渲染当前路由对应的组件
 */
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>
