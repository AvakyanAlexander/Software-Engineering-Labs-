workspace {  

    model {  
        user = person "Исполнитель" {  
            description "Пользователь, создающий и управляющий проектами и задачами."  
        }  

        ProjectSystem = softwareSystem "Система управления проектами" {  
            description "Инструмент управления проектами, который понадобится для планирования, систематизирования задач и отслеживания работы команд."  

            apiGateway = container "API Gateway" {  
                description "Точка входа для всех API запросов."  
                technology "Python / FastAPI / OAuth 2.0 / JWT / CryptContext"  
            }  

            userService = container "Сервис пользователей" {  
                description "Сервис для управления пользователями."  
                technology "Python / FastAPI"  
            }  

            projectService = container "Сервис проектов" {  
                description "Сервис для управления проектами."  
                technology "Python / FastAPI"  
            }  

            taskService = container "Сервис задач" {  
                description "Сервис для управления задачами."  
                technology "Python / FastAPI"  
            }   

            database = container "База Данных" {
                tags "Database"  
                description "База данных для хранения данных о пользователях, проектах и задачах."  
                technology "PostgreSQL"  
            }  
            
            user -> apiGateway "Использует для аутентификации"  
            apiGateway -> userService "Управление пользователями: [создание, поиск по имени и фамилии, поиск по маске]"  
            apiGateway -> projectService "Управление проектами: [создание, поиск по имени проекта, поиск всех проектов]"  
            apiGateway -> taskService "Управление задачами: [создание, по имени задачи, поиск всех задач]"  
            userService -> database "Операции с пользователями: [создание, поиск по имени и фамилии, поиск по маске]ы"  
            projectService -> database "Операции с проектами: [создание, поиск по имени проекта, поиск всех проектов]"  
            taskService -> database "Операции с задачами: [создание, по имени задачи, поиск всех задач]"  
        }    
    }  

    views {  
        systemContext ProjectSystem {  
            include *  
            autolayout lr  
        }  

        container ProjectSystem {  
            include *  
            autolayout lr  
        }  
        dynamic ProjectSystem "login_user" "Регистрация нового пользователя" {  
            user -> apiGateway "Запрос на создание пользователя"  
            apiGateway -> userService "Передает данные  "  
            userService -> database "Создает нового пользователя"  
            database -> userService "Подтверждение создания пользователя, хеширование пароля"  
            userService -> apiGateway "Передача информации"  
            apiGateway -> user "Ответ о регистрации (Успех / ошибка)"  
            autoLayout lr  
        }  
        styles {
        element "Database" {
                shape cylinder
            }
        }
        theme default  
    }  
}  