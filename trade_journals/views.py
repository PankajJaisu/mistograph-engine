from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
import pandas as pd
import openpyxl



@api_view(['POST'])
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
        
        # Find the currency pair with the highest total profit
        most_profitable_pair = profit_by_pair.idxmax()
        highest_profit = profit_by_pair.max()

        return JsonResponse({
            'most_profitable_pair': most_profitable_pair,
            'highest_profit': highest_profit
        }, status=status.HTTP_200_OK)
    except Exception as e:
       
        return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profitable_day(request):
    uploaded_file = request.FILES['report']

    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(uploaded_file)

        # Convert opening_time_utc and profit_inr columns to appropriate data types
        df['opening_time_utc'] = pd.to_datetime(df['opening_time_utc'])
        df['profit_inr'] = pd.to_numeric(df['profit_inr'], errors='coerce')

        # Extract the day of the week and map it to the actual day name
        df['day_of_week'] = df['opening_time_utc'].dt.day_name()

        # Group the trades by day of the week and sum the profits
        profit_by_day = df.groupby('day_of_week')['profit_inr'].sum()
        
        # Find the day of the week with the highest total profit    
        most_profitable_day = profit_by_day.idxmax()
        highest_profit = profit_by_day.max()

        return JsonResponse({
            'most_profitable_day': most_profitable_day,
            'highest_profit': highest_profit
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def analyze_win_percentage(request):
    if 'report' in request.FILES:
        uploaded_file = request.FILES['report']
        file_extension = uploaded_file.name.split('.')[-1].lower()

        try:
            if file_extension == 'csv':
                df = pd.read_csv(uploaded_file)
            elif file_extension == 'xlsx':
                # Load XLSX file using openpyxl
                wb = openpyxl.load_workbook(uploaded_file)
                sheet = wb.active
                data = sheet.values
                cols = next(data)
                df = pd.DataFrame(data, columns=cols)
            else:
                return JsonResponse({'message': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine the profit column based on availability
            profit_column = 'profit_usd' if 'profit_usd' in df.columns else 'profit_inr'

            # Calculate win percentage, most profitable pair, most profitable day, etc.
            total_trades = len(df)
            winning_trades = len(df[df[profit_column] > 0])
            win_percentage = (winning_trades / total_trades) * 100
            profit_by_pair = df.groupby('symbol')[profit_column].sum()
            most_profitable_pair = profit_by_pair.idxmax()
            highest_profit_pair = profit_by_pair.max()
            df['opening_time_utc'] = pd.to_datetime(df['opening_time_utc'])
            df[profit_column] = pd.to_numeric(df[profit_column], errors='coerce')
            df['day_of_week'] = df['opening_time_utc'].dt.day_name()
            profit_by_day = df.groupby('day_of_week')[profit_column].sum()
            most_profitable_day = profit_by_day.idxmax()

            # Risk to Reward calculation
            df = df.dropna(subset=['stop_loss', 'take_profit'])

            # Calculate risk-to-reward ratio for each trade
            df['risk'] = abs(df['opening_price'] - df['stop_loss'])
            df['reward'] = abs(df['take_profit'] - df['opening_price'])
            df['risk_to_reward'] = df['risk'] / df['reward']

            # Calculate average risk-to-reward ratio
            average_risk_to_reward = df['risk_to_reward'].mean()

        

            # Add the session code here:
            # Define session time ranges
            london_session_start = '07:00:00'
            london_session_end = '09:00:00'
            new_york_session_start = '11:30:00'
            new_york_session_end = '15:00:00'

            # Create a function to categorize the session
            def categorize_session(opening_time):
                if london_session_start <= opening_time <= london_session_end:
                    return 'London Session'
                elif new_york_session_start <= opening_time <= new_york_session_end:
                    return 'New York Session'
                

            # Apply the categorize_session function to create a new column 'session'
            df['session'] = df['opening_time_utc'].dt.strftime('%H:%M:%S').apply(categorize_session)

            # Group the data by session and calculate the total profit for each session
            session_profit = df.groupby('session')[profit_column].sum()
            session_profit_dict = session_profit.to_dict()
            print("session_profit: " ,session_profit)
            # Find the session with the highest profit
            most_profitable_session = session_profit.idxmax()
            # highest_profit_session = session_profit.max()

            data = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_percentage': win_percentage,
                'most_profitable_pair': most_profitable_pair,
                'most_profitable_day': most_profitable_day,
                # 'risk_reward': average_risk_to_reward,
                'most_profitable_session': most_profitable_session,
                'london_session_profit': session_profit_dict.get('London Session', 0),
                'new_york_session_profit': session_profit_dict.get('New York Session', 0),

            
            }
            return JsonResponse({
                "message": 'File uploaded successfully',
                "data": data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("error", e)
            return JsonResponse({'message': 'Error processing the file'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
