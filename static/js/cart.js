var updateBtns= document.getElementsByClassName('update-cart')

for (var i=0; i< updateBtns.length;i++){
    updateBtns[i].addEventListener('click',function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        if(action=='add'){
            swal("Item Added", "Item Added to cart", "success")
            // alert("Item Added to cart")
           
        }else{
            swal("Item Removed", "Item removed from  cart", "error")
            // alert("Item removed from  cart")
        }
        
        console.log('productId: ',productId,'Action:',action)
        console.log('User:',user)
        if (user=='AnonymousUser'){
            addCookieItem(productId,action)
        }else{
            updateUserOrder(productId,action)
        } 
    })
}



function addCookieItem(productId,action){
    console.log('user is not logged in')
    
    if(action == 'add'){
       
       
        if (cart[productId] == undefined){
            cart[productId]={'quantity':1}
            
    
        }else{
        cart[productId]['quantity'] +=1
        // product[productId]['quantity'] -=1
        }
    }
    if(action == 'remove'){
        
        cart[productId]['quantity'] -=1
        

        if (cart[productId]['quantity'] <= 0){
            console.log('Item should be deleted')
            delete cart[productId]
        }
    
    }
    document.cookie='cart='+ JSON.stringify(cart)+";domain=;path=/"
    setTimeout(window.location.reload.bind(window.location),1000);
    
}    
    
    

function updateUserOrder(productId,action){
    console.log('User is authenticated, sending data');
    var url = '/update_item/';
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId,'action':action})
    })
    .then((response) =>{
        return response.json();
    })
    .then((data) => {
        console.log('Data:',data)
        setTimeout(window.location.reload.bind(window.location),1000);
    });
}