import { ReactElement } from 'react'
import { Flex, Layout } from 'antd'
import './components/Chatbox'
import ChatBox from './components/Chatbox'
const { Header, Sider, Content } = Layout

const headerStyle: React.CSSProperties = {
  textAlign: 'center',
  color: '#fff',
  height: 'var(--header-height, 64px)',
  paddingInline: 48,
  lineHeight: 'var(--header-height, 64px)',
  backgroundColor: '#4096ff'
}

const contentStyle: React.CSSProperties = {
  textAlign: 'center',
  height: 'calc(100vh - var(--header-height, 64px))',
  lineHeight: '120px',
  color: '#fff'
  // backgroundColor: '#0958d9'
}

const siderStyle: React.CSSProperties = {
  textAlign: 'center',
  lineHeight: '120px',
  width: '280px',
  maxWidth: '280px',
  minWidth: '280px',
  padding: '16px',
  color: '#fff',
  backgroundColor: '#1677ff'
}

const layoutStyle = {
  borderRadius: 8,
  overflow: 'hidden',
  width: '100%',
  height: '100%'
}

const App = (): ReactElement => {
  return (
    <Flex gap="middle" wrap>
      <Layout style={layoutStyle}>
        <Header style={headerStyle}>Header</Header>
        <Layout>
          <Sider width={280} style={siderStyle}>
            Sider2
          </Sider>
          <Content style={contentStyle}>
            123
            {/* <ChatBox /> */}
          </Content>
        </Layout>
        {/* <Footer style={footerStyle}>Footer</Footer> */}
      </Layout>
    </Flex>
  )
}

export default App
