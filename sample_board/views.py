#i-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.utils import timezone
from sample_board.models import DjangoBoard
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

# Create your views here.
# 한글!!
rowsPerPage = 2

def home(request):       # model을 이용해서 별도 SQL 작성 없이 id 필드의 역순으로 (-id) 데이터를 2개만 조회해온다.
	boardList = DjangoBoard.objects.order_by('-id')[0:2]
	current_page =1

      # model 을 사용해서 전체 데이터 갯수를 구한다.
	totalCnt = DjangoBoard.objects.all().count()

      # 이것은 페이징 처리를 위해 생성한 간단한 헬퍼 클래스이다. 별로 중요하지 않으므로 소스를 참조하기 바란다.
	pagingHelperIns = pagingHelper();
	totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
	print 'totalPageList', totalPageList

      # 템플릿으로 필요한 정보들을 넘기는 부분이다. 이를 통해서 정적인 템플릿에 동적인 데이터가 결합되게 되는 것이다.
      # 우리는 게시판 최초 화면 처리를 위해서 listSpecificPage.html 템플릿을 호출했다.
      # 그리고 필요한 정보들을 dictionary 로 전달했다.
	return render_to_response('listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt,'current_page':current_page, 'totalPageList':totalPageList} )

def show_write_form(request):
	return render_to_response('writeBoard.html')

@csrf_exempt
def DoWriteBoard(request):
	br = DjangoBoard(subject = request.POST['subject'],
			name = request.POST['name'],
			mail = request.POST['email'],
			memo = request.POST['memo'],
			created_date = timezone.now(),
			hits = 0
			)
	br.save()
	
	url = '/listSpecificPageWork?current_page=1'
	return HttpResponseRedirect(url);

def listSpecificPageWork(request):
	current_page = int(request.GET['current_page'])
	totalCnt = DjangoBoard.objects.all().count()

	print 'current_page=',current_page
	
	boardList = DjangoBoard.objects.raw('select id, subject, name, created_date, mail, memo,hits from sample_board_djangoboard order by id desc limit %s, %s', [(current_page-1)*rowsPerPage, rowsPerPage])

	print 'boardList=',boardList, 'count()=',totalCnt

	pagingHelperIns = pagingHelper();
	totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)

	print 'totalPageList', totalPageList

	return render_to_response('listSpecificPage.html', {'boardList':boardList,'totalCnt':totalCnt,'current_page':int(current_page),'totalPageList':totalPageList})

def viewWork(request):
	pk = request.GET['memo_id']
	boardData = DjangoBoard.objects.get(id=pk)

	DjangoBoard.objects.filter(id=pk).update(hits = boardData.hits + 1)

	return render_to_response('viewMemo.html', {'memo_id': request.GET['memo_id'], 'current_page':request.GET['current_page'], 'searchStr': request.GET['searchStr'], 'boardData': boardData } )

def listSearchedSpecificPageWork(request):
#    current_page = int(request.GET['current_page'])
    searchStr = request.GET['searchStr']
    pageForView = int(request.GET['pageForView'])

    #print pageForView
    #print 'pageForView : '+str(pageForView)

    # 다음은 테이블에서 subject 항목에 대해 LIKE SQL을 수행한다.
    print '1. searchStr : '+searchStr
    totalCnt = DjangoBoard.objects.filter(subject__contains=searchStr).count()
    print 'pageForView : ' + str(pageForView)
    #print 'totalCnt : '+ str(totalCnt)
    print 'totalCnnnnnT : '+str(totalCnt)

    searchStr = "%"+searchStr+"%"
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList(totalCnt, rowsPerPage)
    
    print 'totalPageList : ' + str(totalPageList)

    # Raw SQL에 like 구문 적용방법.. 이 방법 찾다가 삽질 좀 했다.
    boardList = DjangoBoard.objects.raw('select id, subject, name, created_date, mail, memo,hits from sample_board_djangoboard where subject like %s order by id desc limit %s, %s', [searchStr,(pageForView-1)*rowsPerPage, rowsPerPage])
    searchStr = searchStr.replace("%","")
    return render_to_response('listSearchedSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt, 'pageForView':pageForView ,'searchStr':searchStr, 'totalPageList':totalPageList} )

def listSpecificPageWork_to_update(request):
    memo_id = request.GET['memo_id']
    current_page = request.GET['current_page']
    searchStr = request.GET['searchStr']
    boardData = DjangoBoard.objects.get(id=memo_id)
    return render_to_response('viewForUpdate.html', {'memo_id': request.GET['memo_id'],'current_page':request.GET['current_page'],'searchStr': request.GET['searchStr'],'boardData': boardData } )

@csrf_exempt
def updateBoard(request):
    memo_id = request.POST['memo_id']
    current_page = request.POST['current_page']
    searchStr = request.POST['searchStr']

    # Update DataBase
    DjangoBoard.objects.filter(id=memo_id).update(
                                                  mail= request.POST['mail'],
                                                  subject= request.POST['subject'],
                                                  memo= request.POST['memo']
                                                  )

    # Display Page => POST 요청은 redirection으로 처리하자
    url = '/listSpecificPageWork?current_page=' + str(current_page)
    return HttpResponseRedirect(url)

def DeleteSpecificRow(request):
    memo_id = request.GET['memo_id']
    current_page = request.GET['current_page']

    p = DjangoBoard.objects.get(id=memo_id)
    p.delete()
   
    # 마지막 메모를 삭제하는 경우, 페이지를 하나 줄임.
    totalCnt = DjangoBoard.objects.all().count()
    pagingHelperIns = pagingHelper();

    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    print 'totalPages', totalPageList

    if( int(current_page) in totalPageList):
        print 'current_page No Change'
        current_page=current_page
    else:
        current_page= int(current_page)-1
        print 'current_page--'

    url = '/listSpecificPageWork?current_page=' + str(current_page)
    return HttpResponseRedirect(url)

@csrf_exempt
def searchWithSubject(request):
    searchStr = request.POST['searchStr']
    print 'searchStr', searchStr

    url = '/listSearchedSpecificPageWork?searchStr=' + searchStr +'&pageForView=1'
    return HttpResponseRedirect(url)


class pagingHelper:
    "paging helper class"
    def getTotalPageList(self, total_cnt, rowsPerPage):               
        if ((total_cnt % rowsPerPage) == 0):
            self.total_pages = total_cnt / rowsPerPage;
            print 'getTotalPage #1'
        else:
            self.total_pages = (total_cnt / rowsPerPage) + 1;
            print 'getTotalPage #2'
               
        self.totalPageList = []
        for j in range( self.total_pages ):
            self.totalPageList.append(j+1)
                
        return self.totalPageList        

    def __init__(self ):
        self.total_pages = 0
        self.totalPageList  = 0

