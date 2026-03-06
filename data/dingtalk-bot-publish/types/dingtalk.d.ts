// 钉钉 SDK 类型声明文件

declare module '@alicloud/dingtalk/workflow_1_0' {
  // 获取审批实例 ID 列表
  export class ListProcessInstanceIdsHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ListProcessInstanceIdsHeaders>);
  }

  export class ListProcessInstanceIdsRequest {
    processCode?: string;
    startTime?: number;
    endTime?: number;
    size?: number;
    nextToken?: string;
    constructor(init?: Partial<ListProcessInstanceIdsRequest>);
  }

  export interface ListProcessInstanceIdsResponseBody {
    result?: {
      list?: string[];
      nextToken?: string;
    };
  }

  export interface ListProcessInstanceIdsResponse {
    body?: ListProcessInstanceIdsResponseBody;
  }

  // 获取单个审批实例详情
  export class GetProcessInstanceHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<GetProcessInstanceHeaders>);
  }

  export class GetProcessInstanceRequest {
    processInstanceId?: string;
    constructor(init?: Partial<GetProcessInstanceRequest>);
  }

  export interface GetProcessInstanceResponseBody {
    result?: {
      processInstanceId?: string;
      title?: string;
      createTimeGMT?: string;
      finishTimeGMT?: string;
      originatorUserId?: string;
      originatorDeptId?: string;
      status?: string;
      processCode?: string;
      formComponentValues?: any[];
      operationRecords?: any[];
      tasks?: any[];
    };
  }

  export interface GetProcessInstanceResponse {
    body?: GetProcessInstanceResponseBody;
  }

  // 创建审批实例
  export class CreateProcessInstanceHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<CreateProcessInstanceHeaders>);
  }

  export class CreateProcessInstanceRequest {
    processCode?: string;
    originatorUserId?: string;
    deptId?: string;
    formComponentValues?: any[];
    ccList?: string;
    constructor(init?: Partial<CreateProcessInstanceRequest>);
  }

  export interface CreateProcessInstanceResponseBody {
    result?: {
      processInstanceId?: string;
    };
  }

  export interface CreateProcessInstanceResponse {
    body?: CreateProcessInstanceResponseBody;
  }

  // 终止审批实例
  export class TerminateProcessInstanceHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<TerminateProcessInstanceHeaders>);
  }

  export class TerminateProcessInstanceRequest {
    processInstanceId?: string;
    operatingUserId?: string;
    remark?: string;
    constructor(init?: Partial<TerminateProcessInstanceRequest>);
  }

  export interface TerminateProcessInstanceResponseBody {
    success?: boolean;
  }

  export interface TerminateProcessInstanceResponse {
    body?: TerminateProcessInstanceResponseBody;
  }

  // 执行审批任务
  export class ExecuteTaskHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ExecuteTaskHeaders>);
  }

  export class ExecuteTaskRequest {
    processInstanceId?: string;
    taskId?: string;
    actionerUserId?: string;
    result?: string;
    remark?: string;
    constructor(init?: Partial<ExecuteTaskRequest>);
  }

  export interface ExecuteTaskResponseBody {
    success?: boolean;
  }

  export interface ExecuteTaskResponse {
    body?: ExecuteTaskResponseBody;
  }

  // 添加审批评论
  export class AddProcessInstanceCommentHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<AddProcessInstanceCommentHeaders>);
  }

  export class AddProcessInstanceCommentRequest {
    processInstanceId?: string;
    commentUserId?: string;
    text?: string;
    constructor(init?: Partial<AddProcessInstanceCommentRequest>);
  }

  export interface AddProcessInstanceCommentResponseBody {
    success?: boolean;
  }

  export interface AddProcessInstanceCommentResponse {
    body?: AddProcessInstanceCommentResponseBody;
  }

  // 获取用户待审批数量
  export class GetTodoNumHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<GetTodoNumHeaders>);
  }

  export class GetTodoNumRequest {
    userId?: string;
    constructor(init?: Partial<GetTodoNumRequest>);
  }

  export interface GetTodoNumResponseBody {
    result?: {
      count?: number;
    };
  }

  export interface GetTodoNumResponse {
    body?: GetTodoNumResponseBody;
  }

  // 获取用户待处理审批列表
  export class ListUserTodoProcessInstancesHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ListUserTodoProcessInstancesHeaders>);
  }

  export class ListUserTodoProcessInstancesRequest {
    userId?: string;
    nextToken?: string;
    maxResults?: number;
    constructor(init?: Partial<ListUserTodoProcessInstancesRequest>);
  }

  export interface ListUserTodoProcessInstancesResponseBody {
    result?: {
      data?: any[];
      nextToken?: string;
    };
  }

  export interface ListUserTodoProcessInstancesResponse {
    body?: ListUserTodoProcessInstancesResponseBody;
  }

  // 获取用户已处理审批列表
  export class ListUserDoneProcessInstancesHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ListUserDoneProcessInstancesHeaders>);
  }

  export class ListUserDoneProcessInstancesRequest {
    userId?: string;
    startTime?: number;
    endTime?: number;
    nextToken?: string;
    maxResults?: number;
    constructor(init?: Partial<ListUserDoneProcessInstancesRequest>);
  }

  export interface ListUserDoneProcessInstancesResponseBody {
    result?: {
      data?: any[];
      nextToken?: string;
    };
  }

  export interface ListUserDoneProcessInstancesResponse {
    body?: ListUserDoneProcessInstancesResponseBody;
  }

  // 获取用户发起审批列表
  export class ListUserStartedProcessInstancesHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ListUserStartedProcessInstancesHeaders>);
  }

  export class ListUserStartedProcessInstancesRequest {
    userId?: string;
    startTime?: number;
    endTime?: number;
    nextToken?: string;
    maxResults?: number;
    constructor(init?: Partial<ListUserStartedProcessInstancesRequest>);
  }

  export interface ListUserStartedProcessInstancesResponseBody {
    result?: {
      data?: any[];
      nextToken?: string;
    };
  }

  export interface ListUserStartedProcessInstancesResponse {
    body?: ListUserStartedProcessInstancesResponseBody;
  }

  // 获取用户抄送审批列表
  export class ListUserCcProcessInstancesHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<ListUserCcProcessInstancesHeaders>);
  }

  export class ListUserCcProcessInstancesRequest {
    userId?: string;
    startTime?: number;
    endTime?: number;
    nextToken?: string;
    maxResults?: number;
    constructor(init?: Partial<ListUserCcProcessInstancesRequest>);
  }

  export interface ListUserCcProcessInstancesResponseBody {
    result?: {
      data?: any[];
      nextToken?: string;
    };
  }

  export interface ListUserCcProcessInstancesResponse {
    body?: ListUserCcProcessInstancesResponseBody;
  }

  // Client
  export default class Client {
    constructor(config: any);
    listProcessInstanceIdsWithOptions(
      request: ListProcessInstanceIdsRequest,
      headers: ListProcessInstanceIdsHeaders,
      runtime: any
    ): Promise<ListProcessInstanceIdsResponse>;
    getProcessInstanceWithOptions(
      request: GetProcessInstanceRequest,
      headers: GetProcessInstanceHeaders,
      runtime: any
    ): Promise<GetProcessInstanceResponse>;
    createProcessInstanceWithOptions(
      request: CreateProcessInstanceRequest,
      headers: CreateProcessInstanceHeaders,
      runtime: any
    ): Promise<CreateProcessInstanceResponse>;
    terminateProcessInstanceWithOptions(
      request: TerminateProcessInstanceRequest,
      headers: TerminateProcessInstanceHeaders,
      runtime: any
    ): Promise<TerminateProcessInstanceResponse>;
    executeTaskWithOptions(
      request: ExecuteTaskRequest,
      headers: ExecuteTaskHeaders,
      runtime: any
    ): Promise<ExecuteTaskResponse>;
    addProcessInstanceCommentWithOptions(
      request: AddProcessInstanceCommentRequest,
      headers: AddProcessInstanceCommentHeaders,
      runtime: any
    ): Promise<AddProcessInstanceCommentResponse>;
    getTodoNumWithOptions(
      request: GetTodoNumRequest,
      headers: GetTodoNumHeaders,
      runtime: any
    ): Promise<GetTodoNumResponse>;
    listUserTodoProcessInstancesWithOptions(
      request: ListUserTodoProcessInstancesRequest,
      headers: ListUserTodoProcessInstancesHeaders,
      runtime: any
    ): Promise<ListUserTodoProcessInstancesResponse>;
    listUserDoneProcessInstancesWithOptions(
      request: ListUserDoneProcessInstancesRequest,
      headers: ListUserDoneProcessInstancesHeaders,
      runtime: any
    ): Promise<ListUserDoneProcessInstancesResponse>;
    listUserStartedProcessInstancesWithOptions(
      request: ListUserStartedProcessInstancesRequest,
      headers: ListUserStartedProcessInstancesHeaders,
      runtime: any
    ): Promise<ListUserStartedProcessInstancesResponse>;
    listUserCcProcessInstancesWithOptions(
      request: ListUserCcProcessInstancesRequest,
      headers: ListUserCcProcessInstancesHeaders,
      runtime: any
    ): Promise<ListUserCcProcessInstancesResponse>;
  }
}

declare module '@alicloud/dingtalk/contact_1_0' {
  export class SearchUserHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<SearchUserHeaders>);
  }
  
  export class SearchUserRequest {
    queryWord?: string;
    offset?: number;
    size?: number;
    constructor(init?: Partial<SearchUserRequest>);
  }
  
  export interface SearchUserResponseBody {
    list?: string[];  // 返回的是 userid 列表
    totalCount?: number;
    hasMore?: boolean;
  }
  
  export interface SearchUserResponse {
    body?: SearchUserResponseBody;
  }
  
  export class SearchDepartmentHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<SearchDepartmentHeaders>);
  }

  export class SearchDepartmentRequest {
    queryWord?: string;
    offset?: number;
    size?: number;
    constructor(init?: Partial<SearchDepartmentRequest>);
  }

  export interface SearchDepartmentResponseBody {
    list?: number[];  // 返回的是部门 ID 列表
    totalCount?: number;
    hasMore?: boolean;
  }

  export interface SearchDepartmentResponse {
    body?: SearchDepartmentResponseBody;
  }

  export default class Client {
    constructor(config: any);
    searchUserWithOptions(
      request: SearchUserRequest,
      headers: SearchUserHeaders,
      runtime: any
    ): Promise<SearchUserResponse>;
    searchDepartmentWithOptions(
      request: SearchDepartmentRequest,
      headers: SearchDepartmentHeaders,
      runtime: any
    ): Promise<SearchDepartmentResponse>;
  }
}

declare module '@alicloud/dingtalk/oauth2_1_0' {
  export class GetAccessTokenRequest {
    appKey?: string;
    appSecret?: string;
    constructor(init?: Partial<GetAccessTokenRequest>);
  }
  
  export interface GetAccessTokenResponseBody {
    accessToken?: string;
    expireIn?: number;
  }
  
  export interface GetAccessTokenResponse {
    body?: GetAccessTokenResponseBody;
  }
  
  export default class Client {
    constructor(config: any);
    getAccessToken(request: GetAccessTokenRequest): Promise<GetAccessTokenResponse>;
  }
}

declare module '@alicloud/dingtalk/robot_1_0' {
  export class BatchSendOTOHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<BatchSendOTOHeaders>);
  }

  export class BatchSendOTORequest {
    robotCode?: string;
    userIds?: string[];
    msgKey?: string;
    msgParam?: string;
    constructor(init?: Partial<BatchSendOTORequest>);
  }

  export interface BatchSendOTOResponseBody {
    processQueryKey?: string;
    flowControlledStaffIdList?: string[];
    invalidStaffIdList?: string[];
  }

  export interface BatchSendOTOResponse {
    body?: BatchSendOTOResponseBody;
  }

  export class OrgGroupSendHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<OrgGroupSendHeaders>);
  }

  export class OrgGroupSendRequest {
    openConversationId?: string;
    robotCode?: string;
    msgKey?: string;
    msgParam?: string;
    constructor(init?: Partial<OrgGroupSendRequest>);
  }

  export interface OrgGroupSendResponseBody {
    processQueryKey?: string;
  }

  export interface OrgGroupSendResponse {
    body?: OrgGroupSendResponseBody;
  }

  export class GetBotListInGroupHeaders {
    xAcsDingtalkAccessToken: string;
    constructor(init?: Partial<GetBotListInGroupHeaders>);
  }

  export class GetBotListInGroupRequest {
    openConversationId?: string;
    constructor(init?: Partial<GetBotListInGroupRequest>);
  }

  export interface GetBotListInGroupResponseBody {
    chatbotInstanceVOList?: any[];
  }

  export interface GetBotListInGroupResponse {
    body?: GetBotListInGroupResponseBody;
  }

  export default class Client {
    constructor(config: any);
    batchSendOTOWithOptions(
      request: BatchSendOTORequest,
      headers: BatchSendOTOHeaders,
      runtime: any
    ): Promise<BatchSendOTOResponse>;
    orgGroupSendWithOptions(
      request: OrgGroupSendRequest,
      headers: OrgGroupSendHeaders,
      runtime: any
    ): Promise<OrgGroupSendResponse>;
    getBotListInGroupWithOptions(
      request: GetBotListInGroupRequest,
      headers: GetBotListInGroupHeaders,
      runtime: any
    ): Promise<GetBotListInGroupResponse>;
  }
}
