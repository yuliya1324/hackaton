from DefineSkills import define_skills
from PredictOccupation import predict_occupation

if __name__ == '__main__':

    print("Выберите опцию и нажмите цифру:")
    print("1 - Выбрать профессию и узнать какие навыки необходимо улучшить")
    print("2 - Отметить имеющиеся навыки и узнать подходящую профессию")
    ans = int(input('Введите цифру: '))

    if ans == 1:
        define_skills()
    if ans == 2:
        print(f"Вам больше всего подходит профессия {predict_occupation()}")
