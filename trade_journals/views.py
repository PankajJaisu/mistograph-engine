from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import pandas as pd



@api_view(['GET'])
def win_percentage(request):
    print(request.FILES.get('report'))
  
    uploaded_file = request.FILES.get('report')
    try:
     
        df = pd.read_csv(uploaded_file)

        total_trades = len(df)
        winning_trades = len(df[df['profit_inr'] > 0])
        win_percentage = (winning_trades / total_trades) * 100
        return JsonResponse({
                    'message': 'File uploaded successfully',
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'win_percentage': win_percentage
                }, status=status.HTTP_201_CREATED)
    except Exception as e:
            return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def profitable_pair(request):
    try:
        uploaded_file = request.FILES.get('report')
        df = pd.read_csv(uploaded_file)

        # Group the trades by currency pair and sum the profits
        profit_by_pair = df.groupby('symbol')['profit_inr'].sum()
        print(profit_by_pair)
        # Find the currency pair with the highest total profit
        most_profitable_pair = profit_by_pair.idxmax()
        highest_profit = profit_by_pair.max()

        return JsonResponse({
            'most_profitable_pair': most_profitable_pair,
            'highest_profit': highest_profit
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)
