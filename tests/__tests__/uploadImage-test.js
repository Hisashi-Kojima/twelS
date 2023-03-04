/**
 * @jest-environment jsdom
 */

//Test対象のHTML
const html = `
    <button type="button" onclick="uploadImage()" id="camera">
        <img src="{% static 'search/images/camera.png' %}" width="30" />
    </button>
    <form id="imageForm" method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <input type="file" name="uploadImage" accept="image/*" id="uploadImage" style="display: none">
    </form>
`

//Test対象の関数
function uploadImage() {
    const uploadImageBtn = document.getElementById('uploadImage');
    // for camera: setting a event which a file input was changed.
    uploadImageBtn.addEventListener(
        "change",
        (e) => {// when the file uploaded, the form is posted py this code.
            const imageForm = document.getElementById('imageForm');
            imageForm.submit();
        }
    )
    uploadImageBtn.click();
}


describe('uploadImage()のテスト', ()=> {
    let cameraBtn;
    let uploadImageBtn;
    let clickSpy;
    let addEventListenerSpy;
    beforeAll(() => {
        document.body.innerHTML = html;
        cameraBtn = document.getElementById('camera');
        uploadImageBtn = document.getElementById('uploadImage');
        clickSpy = jest.spyOn(uploadImageBtn, 'click');
        addEventListenerSpy = jest.spyOn(uploadImageBtn, 'addEventListener');
    })
    //各テスト毎にここの部分が実行される．
    beforeEach(() => {
        uploadImage();
    })

    test('cameraボタンが取得できているか', () => {
        expect(cameraBtn).toBeDefined();
        expect(cameraBtn).not.toBeNull();
    })

    //changeイベントが付与できたかを確認する．
    test('input要素にchangeイベントを付与できたか', () => {
        expect(addEventListenerSpy).toBeCalledWith('change', expect.any(Function));
    })

    //clickイベントが発火したかを確認する．
    test('input要素が間接的にclickされたか', () => {
        expect(clickSpy).toBeCalled();
    })
})