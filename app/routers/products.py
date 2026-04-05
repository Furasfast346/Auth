from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from app.schemas import ProductCreate, ProductUpdate
from app.dependencies import SessionDep, require_permission
from app.models import User, Product
from sqlalchemy import select

router = APIRouter()


@router.get('/')
async def get_products(session: SessionDep, current_user: User = Depends(require_permission('products:read'))):
    result = await session.execute(select(Product))
    return result.scalars().all()


@router.post('/')
async def create_product(data: ProductCreate, session: SessionDep,
                         current_user: User = Depends(require_permission('products:write'))):
    new_product = Product(name=data.name, price=data.price, in_stock=data.in_stock)
    session.add(new_product)
    await session.commit()
    await session.refresh(new_product)
    return new_product


@router.get('/{product_id}')
async def get_product(product_id: int, session: SessionDep,
                      current_user: User = Depends(require_permission('products:read'))):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(404, 'Product not found')

    return product


@router.put('/{product_id}')
async def edit_product(product_id: int, data: ProductUpdate, session: SessionDep,
                       current_user: User = Depends(require_permission('products:write'))):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(404, 'Product not found')

    product.name = data.name
    product.in_stock = data.in_stock
    product.price = data.price

    await session.commit()
    await session.refresh(product)
    return product

@router.delete('/{product_id}')
async def delete_product(product_id: int, session: SessionDep,
                       current_user: User = Depends(require_permission('products:delete'))):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(404, 'Product not found')

    await session.delete(product)
    await session.commit()
    return {'message' : 'Product was deleted'}