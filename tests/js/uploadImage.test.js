/**
 * @jest-environment jsdom
 */

//Test対象のHTML
const fs = require('fs');
const path = require('path');
const htmlRelativePath = '../.././front/search/templates/search/index.html';
const htmlAbsolutePath = path.resolve(__dirname, htmlRelativePath);
const html = fs.readFileSync(htmlAbsolutePath, { encoding: 'utf-8'});

//Test対象の関数
const functionRelativePath = '../.././front/static/js/mathpix/uploadImage.js';
const functionAbsolutePath = path.resolve(__dirname, functionRelativePath);
const uploadedImageFunction = require(functionAbsolutePath);

describe('uploadImage()のテスト', ()=> {
    let cameraBtn;
    let uploadImageBtn;
    let clickSpy;
    let addEventListenerSpy;
    //全体の実行前にここの部分が実行される.
    beforeAll(() => {
        document.body.innerHTML = html;
        cameraBtn = document.getElementById('camera');
        uploadImageBtn = document.getElementById('uploadImage');
        clickSpy = jest.spyOn(uploadImageBtn, 'click');
        addEventListenerSpy = jest.spyOn(uploadImageBtn, 'addEventListener');
    })
    //各テスト毎にここの部分が実行される．
    beforeEach(() => {
        uploadedImageFunction();
    })

    test('cameraボタンが取得できているか', () => {
        expect(cameraBtn).toBeDefined();
        expect(cameraBtn).not.toBeNull();
    })

    test('input要素にchangeイベントを付与できたか', () => {
        expect(addEventListenerSpy).toBeCalledWith('change', expect.any(Function));
    })

    test('input要素が間接的にclickされたか', () => {
        expect(clickSpy).toBeCalled();
    })
})